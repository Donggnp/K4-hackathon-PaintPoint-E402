"""Test cho chính backend VLearn.

Chạy:  cd codebase && python3 -m pytest tests/ -v

Các test đụng tới Docker được đánh dấu và tự bỏ qua nếu máy không có Docker,
để bộ test vẫn chạy được ở môi trường CI không có Docker daemon.
"""

import base64
import copy
import io
import json
import os
import sys
import zipfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vlearn.auditors import audit_repo, audit_tutorial
from vlearn.config import MAX_LOGIC_LINES, MIN_LOGIC_LINES
from vlearn.extractors import extract_readme_summary
from vlearn.packaging import (
    count_logic_lines,
    derive_starter_kit,
    files_to_zip_base64,
    is_starter_kit_file,
    zip_base64_to_files,
)
from vlearn.quality import (
    check_explanation_ratio,
    measure_step_balance,
    normalize_lab,
    verify_tutorial_matches_repo,
)
from vlearn.security import security_scan
from vlearn.testrunner import docker_status, run_repo_tests

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

with open(os.path.join(FIXTURES, 'golden-labs.json'), encoding='utf-8') as f:
    GOLDEN_LABS = json.load(f)

docker_ready = docker_status()
needs_docker = pytest.mark.skipif(
    not (docker_ready['available'] and docker_ready['image_ready']),
    reason=f"Cần sandbox Docker: {docker_ready.get('reason')}",
)


@pytest.fixture(params=GOLDEN_LABS, ids=lambda lab: lab['repoName'])
def golden(request):
    """Bài mẫu đã được dựng và chạy pytest thật — chuẩn để đối chiếu."""
    return copy.deepcopy(request.param)


# --- Bài mẫu phải đạt MỌI chốt chặn -----------------------------------------

def test_golden_passes_repo_audit(golden):
    assert audit_repo(golden) == []


def test_golden_passes_tutorial_audit(golden):
    assert audit_tutorial(golden) == []


def test_golden_tutorial_matches_repo_exactly(golden):
    problems = verify_tutorial_matches_repo(
        golden['repo']['files'], golden['steps'], golden['starterKit'])
    assert problems == []


def test_golden_meets_explanation_ratio(golden):
    assert check_explanation_ratio(golden['steps']) == []


def test_golden_has_no_quality_warnings(golden):
    normalize_lab(golden)
    assert golden['qualityWarnings'] == []


def test_golden_logic_lines_in_range(golden):
    loc = count_logic_lines(golden['repo']['files'], golden['starterKit'])
    assert MIN_LOGIC_LINES <= loc <= MAX_LOGIC_LINES


def test_golden_starts_with_step_zero(golden):
    assert golden['steps'][0]['num'] == 0
    assert golden['steps'][0]['title'].startswith('Bước 0')


def test_step_zero_teaches_no_logic_file(golden):
    kit = set(golden['starterKit'])
    for block in golden['steps'][0]['blocks']:
        if block.get('type') == 'code' and block.get('filename'):
            assert block['filename'] in kit


# --- Chốt chặn phải BẮT được lỗi thật ----------------------------------------

def test_detects_tutorial_drift_from_repo(golden):
    target = next(f for f in golden['repo']['files'] if f['path'].endswith('main.py'))
    target['content'] += '\n# Coach sửa\n'
    problems = verify_tutorial_matches_repo(
        golden['repo']['files'], golden['steps'], golden['starterKit'])
    assert len(problems) == 1
    assert 'LỆCH' in problems[0]


def test_detects_thin_explanation(golden):
    step = next(s for s in golden['steps'] if s['num'] == 1)
    for b in step['blocks']:
        if b.get('type') in ('text', 'callout'):
            b['content'] = '<p>ngắn.</p>'
    problems = check_explanation_ratio(golden['steps'])
    assert any('Bước 1' in p for p in problems)


def test_detects_missing_init_file(golden):
    golden['repo']['files'] = [f for f in golden['repo']['files']
                               if not f['path'].endswith('/__init__.py')]
    assert any('__init__.py' in p for p in audit_repo(golden))


def test_detects_ghost_file_in_tree(golden):
    for step in golden['steps']:
        for b in step.get('blocks', []):
            if b.get('type') == 'tree':
                b['items'].append('  src/khong_ton_tai.py')
                break
    assert any('không có thật' in p for p in audit_tutorial(golden))


@pytest.mark.parametrize('code,marker', [
    ('import subprocess\nsubprocess.run(["ls"])\n', 'subprocess'),
    ('import os\nos.remove("/etc/passwd")\n', 'remove'),
    ('eval("1+1")\n', 'eval'),
    ('import socket\ns = socket.socket()\n', 'socket'),
    ('open("/tmp/x", "w")\n', 'ghi'),
])
def test_security_scan_blocks_dangerous_code(code, marker):
    problems = security_scan([{'path': 'src/evil.py', 'content': code}])
    assert problems, f"không chặn được: {marker}"
    assert all(p.startswith('BẢO MẬT') for p in problems)


def test_security_scan_allows_clean_code(golden):
    assert security_scan(golden['repo']['files']) == []


# --- Đóng gói / mở gói -------------------------------------------------------

def test_zip_round_trip_is_lossless(golden):
    files = golden['repo']['files']
    b64 = files_to_zip_base64(files, golden['repoName'])
    back = zip_base64_to_files(b64)
    assert {f['path']: f['content'] for f in back} == {f['path']: f['content'] for f in files}


def test_starter_kit_excludes_every_logic_file(golden):
    kit = set(derive_starter_kit(golden['repo']['files']))
    logic = {f['path'] for f in golden['repo']['files']} - kit
    assert logic, "phải có file logic để học viên tự viết"
    assert not (kit & logic)
    assert all(not is_starter_kit_file(p) for p in logic)


def test_starter_kit_zip_contains_only_kit_files(golden):
    kit = golden['starterKit']
    b64 = files_to_zip_base64(
        [f for f in golden['repo']['files'] if f['path'] in set(kit)], 'kit')
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(b64))) as zf:
        inside = {n[len('kit/'):] for n in zf.namelist()}
    assert inside == set(kit)


# --- Đọc README thay cho .zip ------------------------------------------------

def test_readme_summary_keeps_content_and_labels_source():
    block, label = extract_readme_summary('# Lab\nMục tiêu: dựng agent.', 'README.md')
    assert 'Mục tiêu: dựng agent.' in block
    assert 'README.md' == label
    assert 'không nạp toàn bộ mã nguồn' in block


def test_readme_summary_truncates_when_too_long():
    block, _ = extract_readme_summary('x' * 50000)
    assert 'cắt bớt' in block
    assert len(block) < 20000


# --- Sandbox Docker ----------------------------------------------------------

@needs_docker
def test_golden_repo_passes_tests_in_sandbox(golden):
    report = run_repo_tests(golden['repo']['files'])
    assert report['sandbox'] == 'docker'
    assert report['returncode'] == 0, report['fullOutput'][-2000:]
    assert report['passed'] == report['total'] > 0
    assert len(report['cases']) == report['passed']
    assert all(c['outcome'] == 'PASSED' for c in report['cases'])


@needs_docker
def test_sandbox_reports_failing_tests_with_traceback(golden):
    # Phá một module mà bộ test THỰC SỰ import. main.py là CLI, không test nào
    # đụng tới nó, nên phá main.py sẽ không làm pytest đỏ.
    target = next(f for f in golden['repo']['files']
                  if f['path'].startswith('src/')
                  and f['path'].endswith('.py')
                  and not f['path'].endswith('__init__.py'))
    target['content'] += '\nraise RuntimeError("hỏng có chủ ý")\n'

    report = run_repo_tests(golden['repo']['files'])
    assert report['returncode'] != 0
    assert report['failed'] > 0
    assert 'hỏng có chủ ý' in report['fullOutput']


@needs_docker
def test_sandbox_blocks_filesystem_damage():
    """Mã cố xoá file hệ thống phải bị container chặn."""
    files = [
        {'path': 'pytest.ini', 'content': '[pytest]\ntestpaths = tests\npythonpath = .\n'},
        {'path': 'tests/__init__.py', 'content': ''},
        {'path': 'tests/test_evil.py', 'content':
            'import os, subprocess\n\n'
            'def test_host_is_protected():\n'
            '    subprocess.run(["rm", "-rf", "/etc/hostname"], capture_output=True)\n'
            '    assert os.path.exists("/etc/hostname")\n'},
    ]
    report = run_repo_tests(files)
    assert report['returncode'] == 0, "container KHÔNG bảo vệ được hệ thống file gốc"


@needs_docker
def test_sandbox_has_no_network():
    files = [
        {'path': 'pytest.ini', 'content': '[pytest]\ntestpaths = tests\npythonpath = .\n'},
        {'path': 'tests/__init__.py', 'content': ''},
        {'path': 'tests/test_net.py', 'content':
            'import socket\n\n'
            'def test_network_is_cut():\n'
            '    socket.setdefaulttimeout(3)\n'
            '    try:\n'
            '        socket.create_connection(("1.1.1.1", 53))\n'
            '        assert False, "container VAN co mang"\n'
            '    except OSError:\n'
            '        pass\n'},
    ]
    report = run_repo_tests(files)
    assert report['returncode'] == 0, report['fullOutput'][-1500:]


# --- Chốt chặn ở tầng server -------------------------------------------------

def _tests_green(lab):
    """Bản sao logic đánh giá test trong http_api.handle_generate_tutorial."""
    r = lab.get('testReport') or {}
    return bool(r.get('ran') and not r.get('timedOut')
                and r.get('returncode') == 0 and r.get('passed', 0) > 0)


def _needs_confirmation(lab, allow_failing=False):
    """Có phải hỏi lại Coach trước khi sinh tutorial không?

    Test đỏ KHÔNG chặn — Coach là người quyết định. Hệ thống chỉ cảnh báo và
    bắt xác nhận, rồi ghi dấu lại.
    """
    return not _tests_green(lab) and not allow_failing


def test_asks_confirmation_when_tests_never_ran(golden):
    golden.pop('testReport', None)
    assert _needs_confirmation(golden) is True


def test_asks_confirmation_when_tests_fail(golden):
    golden['testReport'] = {'ran': True, 'returncode': 1, 'passed': 23, 'total': 26}
    assert _needs_confirmation(golden) is True


def test_proceeds_when_coach_confirms_despite_red_tests(golden):
    golden['testReport'] = {'ran': True, 'returncode': 1, 'passed': 23, 'total': 26}
    assert _needs_confirmation(golden, allow_failing=True) is False


def test_no_confirmation_needed_when_all_green(golden):
    golden['testReport'] = {'ran': True, 'returncode': 0, 'passed': 26, 'total': 26}
    assert _needs_confirmation(golden) is False


def test_lab_generated_from_red_tests_is_flagged_in_warnings(golden):
    golden['generatedFromFailingTests'] = {'passed': 23, 'total': 26, 'ran': True}
    normalize_lab(golden)
    assert any('test ĐỎ' in w for w in golden['qualityWarnings'])


def test_history_records_that_repo_had_red_tests(golden, runs_dir):
    from vlearn.history import save_run
    golden['generatedFromFailingTests'] = {'passed': 23, 'total': 26, 'ran': True}
    m = save_run(golden, 'tutorial')
    assert m['generatedFromFailingTests']['passed'] == 23


def test_failing_tests_produce_quality_warning(golden):
    golden['testReport'] = {'ran': True, 'returncode': 1, 'passed': 23, 'total': 26}
    normalize_lab(golden)
    assert any('KHÔNG pass hết test' in w for w in golden['qualityWarnings'])


# --- Lịch sử lượt chạy -------------------------------------------------------

@pytest.fixture
def runs_dir(tmp_path, monkeypatch):
    """Trỏ RUNS_DIR sang thư mục tạm để test không đụng lịch sử thật."""
    import vlearn.history as H
    monkeypatch.setattr(H, 'RUNS_DIR', str(tmp_path / 'runs'))
    return tmp_path / 'runs'


def test_save_run_writes_readable_repo_tree(golden, runs_dir):
    from vlearn.history import save_run
    m = save_run(golden, 'tutorial', {'usage': {'model': 'x', 'rounds': 1, 'totalTokens': 100}})

    assert m and m['runId']
    root = runs_dir / m['runId']
    assert (root / 'manifest.json').is_file()
    assert (root / 'lab.json').is_file()
    assert (root / 'tutorial.md').is_file()

    # repo phải là cây thư mục THẬT, không phải một cục JSON
    for f in golden['repo']['files']:
        assert (root / 'repo' / f['path']).is_file(), f['path']
        assert (root / 'repo' / f['path']).read_text(encoding='utf-8') == f['content']


def test_saved_repo_actually_runs_pytest(golden, runs_dir):
    """Thư mục lưu ra phải chạy được ngay — đó là lý do lưu dạng cây."""
    import subprocess
    from vlearn.history import save_run
    m = save_run(golden, 'repo')
    proc = subprocess.run([sys.executable, '-m', 'pytest', '-q'],
                          cwd=str(runs_dir / m['runId'] / 'repo'),
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout[-1500:]


def test_manifest_records_test_status(golden, runs_dir):
    from vlearn.history import save_run
    golden['testReport'] = {'ran': True, 'returncode': 0, 'passed': 45,
                            'total': 45, 'sandbox': 'docker'}
    m = save_run(golden, 'repo')
    assert m['tests']['state'] == 'passed'
    assert '45/45' in m['tests']['label']

    golden['testReport'] = {'ran': True, 'returncode': 1, 'passed': 23, 'total': 26}
    assert save_run(golden, 'repo')['tests']['state'] == 'failed'

    golden.pop('testReport')
    assert save_run(golden, 'repo')['tests']['state'] == 'not_run'


def test_list_and_load_and_delete_round_trip(golden, runs_dir):
    from vlearn.history import delete_run, list_runs, load_run, save_run
    m = save_run(golden, 'tutorial')

    runs = list_runs()
    assert any(r['runId'] == m['runId'] for r in runs)

    back = load_run(m['runId'])
    assert back['title'] == golden['title']
    assert len(back['repo']['files']) == len(golden['repo']['files'])
    assert len(back['steps']) == len(golden['steps'])

    assert delete_run(m['runId']) is True
    assert load_run(m['runId']) is None
    assert not any(r['runId'] == m['runId'] for r in list_runs())


def test_tutorial_markdown_has_every_step_and_code(golden, runs_dir):
    from vlearn.history import save_run
    m = save_run(golden, 'tutorial')
    md = (runs_dir / m['runId'] / 'tutorial.md').read_text(encoding='utf-8')

    for step in golden['steps']:
        assert step['title'] in md
    taught = {b['filename'] for s in golden['steps'] for b in s['blocks']
              if b.get('type') == 'code' and b.get('filename')}
    for path in taught:
        assert path in md


def test_save_run_rejects_path_escape(runs_dir):
    """Đường dẫn kiểu ../../etc không được ghi ra ngoài thư mục lượt chạy."""
    from vlearn.history import save_run
    lab = {'repoName': 'evil', 'repo': {'files': [
        {'path': '../../../tmp/vlearn_escape.txt', 'content': 'x'},
        {'path': 'ok.py', 'content': 'y'},
    ]}}
    m = save_run(lab, 'repo')
    assert (runs_dir / m['runId'] / 'repo' / 'ok.py').is_file()
    assert not os.path.exists('/tmp/vlearn_escape.txt')


def test_save_run_never_raises_on_bad_input(runs_dir):
    from vlearn.history import save_run
    assert save_run({}, 'repo') is not None          # lab rỗng vẫn lưu được


# --- Khi nào ĐƯỢC/KHÔNG được chạy test ---------------------------------------

@needs_docker
def test_scale_problem_does_not_block_test_run():
    """Repo quá ngắn nhưng CÚ PHÁP HỢP LỆ thì pytest vẫn chạy được — và phải chạy.

    Coach cần bằng chứng hành vi ngay cả khi bài chưa đủ dày, còn lõi cần biết
    code mình có đúng không để sửa cho trúng.
    """
    lab = {'repoName': 'tiny', 'starterKit': [], 'repo': {'files': [
        {'path': 'pytest.ini', 'content': '[pytest]\ntestpaths = tests\npythonpath = .\n'},
        {'path': 'requirements.txt', 'content': 'pytest\n'},
        {'path': 'README.md', 'content': '# tiny\n'},
        {'path': 'main.py', 'content': 'from src.core.calc import add\n\nprint(add(1, 2))\n'},
        {'path': 'config/__init__.py', 'content': ''},
        {'path': 'config/settings.py', 'content': 'STEP = 1\n'},
        {'path': 'src/__init__.py', 'content': ''},
        {'path': 'src/core/__init__.py', 'content': ''},
        {'path': 'src/core/calc.py', 'content':
            'def add(a, b):\n    """Cộng hai số."""\n    return a + b\n'},
        {'path': 'tests/__init__.py', 'content': ''},
        {'path': 'tests/test_calc.py', 'content':
            'from src.core.calc import add\n\n\ndef test_add():\n    assert add(1, 2) == 3\n'},
    ]}}

    problems = audit_repo(lab)
    assert any('dòng logic' in p for p in problems), "phải bắt được lỗi quy mô"
    assert not any('sai cú pháp' in p for p in problems), "repo này cú pháp hợp lệ"
    assert lab['testReport']['ran'] is True, "lỗi quy mô KHÔNG được chặn việc chạy test"
    assert lab['testReport']['returncode'] == 0, lab['testReport'].get('fullOutput', '')[-600:]


@needs_docker
def test_syntax_error_blocks_test_run(golden):
    target = next(f for f in golden['repo']['files']
                  if f['path'].startswith('src/') and not f['path'].endswith('__init__.py'))
    target['content'] = 'def f(\n  pass'

    audit_repo(golden)
    assert golden['testReport']['ran'] is False


@needs_docker
def test_missing_imported_module_blocks_test_run(golden):
    victim = next(f['path'] for f in golden['repo']['files']
                  if f['path'].startswith('src/') and not f['path'].endswith('__init__.py'))
    golden['repo']['files'] = [f for f in golden['repo']['files'] if f['path'] != victim]

    audit_repo(golden)
    assert golden['testReport']['ran'] is False


# --- Chạy THẬT closure work() của endpoint ------------------------------------
# Bộ test cũ chỉ kiểm một BẢN SAO logic, nên đã để lọt lỗi thật:
# `work(report)` che mất biến `report` là dict báo cáo test -> AttributeError.
# Các test dưới đây gọi đúng handler thật (chỉ thay lời gọi OpenAI bằng hàm giả).

class _FakeHandler:
    """Gọi được method của VLearnRequestHandler mà không cần dựng socket."""

    def __init__(self):
        self.responses = []

    def send_json_response(self, data, status=200):
        self.responses.append((status, data))


def _invoke_tutorial(payload, monkeypatch, fake_steps=None):
    import vlearn.http_api as api

    monkeypatch.setattr(api, 'build_tutorial',
                        lambda lab, model, report=None: (fake_steps or [{'num': 0, 'title': 'Bước 0 — x', 'blocks': []}], [{'round': 1, 'violations': [], 'passed': True, 'usage': {}}]))
    monkeypatch.setattr(api, 'save_run', lambda *a, **k: {'runId': 'test-run'})
    # chạy thẳng ở luồng hiện tại để test bắt được exception
    monkeypatch.setattr(api, 'run_in_background',
                        lambda job_id, fn: fn(lambda *a, **k: None))

    handler = _FakeHandler()
    api.VLearnRequestHandler.handle_generate_tutorial(handler, payload)
    return handler.responses[-1]


def test_tutorial_endpoint_asks_confirmation_on_red_tests(golden, monkeypatch):
    golden['testReport'] = {'ran': True, 'returncode': 1, 'passed': 27, 'total': 28}
    status, body = _invoke_tutorial({'lab': golden}, monkeypatch)

    assert status == 409
    assert body['needsConfirmation'] is True
    assert body['testSummary']['passed'] == 27


def test_tutorial_endpoint_runs_when_coach_confirms(golden, monkeypatch):
    """Đây là ca đã từng nổ AttributeError vì trùng tên biến `report`."""
    golden['testReport'] = {'ran': True, 'returncode': 1, 'passed': 27, 'total': 28}
    status, body = _invoke_tutorial(
        {'lab': golden, 'allowFailingTests': True}, monkeypatch)

    assert status == 200, body
    assert body['success'] is True
    assert body['lab']['generatedFromFailingTests'] == {
        'passed': 27, 'total': 28, 'ran': True}


def test_tutorial_endpoint_clears_flag_when_tests_green(golden, monkeypatch):
    golden['testReport'] = {'ran': True, 'returncode': 0, 'passed': 28, 'total': 28}
    golden['generatedFromFailingTests'] = {'passed': 1, 'total': 2, 'ran': True}

    status, body = _invoke_tutorial({'lab': golden}, monkeypatch)

    assert status == 200
    assert 'generatedFromFailingTests' not in body['lab']


def test_tutorial_endpoint_rejects_empty_repo(monkeypatch):
    status, body = _invoke_tutorial({'lab': {'repo': {'files': []}}}, monkeypatch)
    assert status == 400
    assert 'Chưa có repo' in body['error']
