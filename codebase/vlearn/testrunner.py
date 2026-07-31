"""Chạy THẬT pytest trên repo do lõi sinh ra — trong Docker container cách ly.

Vì sao BẮT BUỘC phải là Docker chứ không phải subprocess trên máy thật?
Code này do một mô hình ngôn ngữ viết ra, từ nội dung slide và repo mà người
ngoài nạp lên. Dù đã quét tĩnh bằng `ast` (xem security.py), quét tĩnh không bao
giờ bắt hết được: chỉ cần một cách gọi gián tiếp mà bộ quét chưa biết là mã độc
lọt xuống máy thật. Container cho ta ranh giới cứng ở tầng hệ điều hành:

    --network none          không có mạng, không tải về được gì
    --read-only             hệ thống file gốc chỉ đọc
    --tmpfs /tmp            chỗ ghi tạm nằm trong RAM, mất khi container tắt
    --memory / --cpus       chặn ngốn hết tài nguyên máy
    --pids-limit            chặn fork bomb
    --cap-drop ALL          bỏ mọi quyền đặc biệt của Linux
    --security-opt no-new-privileges
    user không phải root    (đã đặt trong Dockerfile)

Mã có `rm -rf /` thì cũng chỉ xoá được chính container của nó.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

from .config import (
    DOCKER_IMAGE,
    ENABLE_TEST_RUNNER,
    MAX_TEST_OUTPUT_CHARS,
    SANDBOX_CPUS,
    SANDBOX_MEMORY,
    SANDBOX_PIDS_LIMIT,
    TEST_RUN_TIMEOUT_SECONDS,
    UNSAFE_ALLOW_HOST_TESTS,
)

_docker_state = {'checked': False, 'available': False, 'image_ready': False, 'reason': ''}


def _run(cmd, timeout=60, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          errors='replace', **kwargs)


def docker_status(force=False):
    """Docker có dùng được không, và ảnh sandbox đã sẵn sàng chưa.

    Kết quả được nhớ lại vì hàm này bị gọi ở mỗi vòng tự sửa; hỏi Docker mỗi lần
    sẽ thêm cả giây vào mỗi lượt mà chẳng được gì.
    """
    if _docker_state['checked'] and not force:
        return _docker_state

    _docker_state.update(checked=True, available=False, image_ready=False)

    if not shutil.which('docker'):
        _docker_state['reason'] = "Không tìm thấy lệnh `docker` trong PATH."
        return _docker_state

    try:
        info = _run(['docker', 'info', '--format', '{{.ServerVersion}}'], timeout=20)
    except subprocess.TimeoutExpired:
        _docker_state['reason'] = "Docker daemon không phản hồi (quá 20 giây)."
        return _docker_state

    if info.returncode != 0:
        detail = (info.stderr or info.stdout or '').strip().splitlines()
        _docker_state['reason'] = (
            "Docker daemon chưa chạy, hoặc user hiện tại không có quyền. "
            + (detail[-1] if detail else '')
        )
        return _docker_state

    _docker_state['available'] = True
    _docker_state['version'] = (info.stdout or '').strip()

    images = _run(['docker', 'images', '-q', DOCKER_IMAGE], timeout=20)
    _docker_state['image_ready'] = bool((images.stdout or '').strip())
    _docker_state['reason'] = '' if _docker_state['image_ready'] else \
        f"Chưa có ảnh sandbox '{DOCKER_IMAGE}'."

    return _docker_state


def build_sandbox_image():
    """Dựng ảnh sandbox từ sandbox/Dockerfile. Chỉ cần chạy một lần."""
    ctx = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sandbox')
    if not os.path.isdir(ctx):
        return False, f"Không tìm thấy thư mục {ctx}"

    try:
        built = _run(['docker', 'build', '-t', DOCKER_IMAGE, ctx], timeout=900)
    except subprocess.TimeoutExpired:
        return False, "Dựng ảnh sandbox quá 15 phút — kiểm tra kết nối mạng."

    if built.returncode != 0:
        tail = (built.stderr or built.stdout or '').strip().splitlines()[-5:]
        return False, "Dựng ảnh thất bại: " + " / ".join(tail)

    docker_status(force=True)
    return True, f"Đã dựng ảnh sandbox '{DOCKER_IMAGE}'."


def _write_repo(files, workdir):
    """Ghi repo ra đĩa, chặn đường dẫn thoát ra ngoài thư mục tạm."""
    root = os.path.abspath(workdir)
    for f in files:
        path = (f.get('path') or '').lstrip('/')
        if not path:
            continue
        full = os.path.normpath(os.path.join(root, path))
        if not full.startswith(root + os.sep):
            raise ValueError(f"Đường dẫn file không hợp lệ: {path}")
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as fh:
            fh.write(f.get('content') or '')


def _parse_pytest_output(output, returncode, command_label):
    """Bóc số liệu từ output pytest, GIỮ NGUYÊN toàn bộ log để Coach đọc.

    Coach cần thấy tên từng test đã pass, không chỉ con số tổng — đó là bằng
    chứng cụ thể để họ yên tâm bấm duyệt.
    """
    text = output or ''
    passed = int(m.group(1)) if (m := re.search(r'(\d+) passed', text)) else 0
    failed = int(m.group(1)) if (m := re.search(r'(\d+) failed', text)) else 0
    errors = int(m.group(1)) if (m := re.search(r'(\d+) error', text)) else 0
    summary = next((l for l in reversed(text.strip().splitlines()) if l.strip()), '')

    cases = []
    for line in text.splitlines():
        m = re.match(r'^(\S+\.py)::(\S+?)\s+(PASSED|FAILED|ERROR|SKIPPED)', line.strip())
        if m:
            cases.append({"file": m.group(1), "test": m.group(2), "outcome": m.group(3)})

    return {
        "ran": True,
        "timedOut": False,
        "returncode": returncode,
        "passed": passed,
        "failed": failed + errors,
        "total": passed + failed + errors,
        "summary": summary,
        "cases": cases,
        "command": command_label,
        "output": text[-MAX_TEST_OUTPUT_CHARS:],
        "fullOutput": text,
    }


def run_repo_tests(files):
    """Ghi repo ra thư mục tạm rồi chạy `pytest -v` trong Docker container.

    Không bao giờ ném exception ra ngoài: hỏng test-runner thì cũng không được
    làm sập cả luồng sinh bài.
    """
    if not ENABLE_TEST_RUNNER:
        return {"ran": False, "sandbox": "off",
                "reason": "Test-runner đang tắt (VLEARN_RUN_TESTS=0)."}

    status = docker_status()

    if status['available'] and status['image_ready']:
        return _run_in_docker(files)

    if not UNSAFE_ALLOW_HOST_TESTS:
        return {
            "ran": False,
            "sandbox": "unavailable",
            "reason": (
                f"Sandbox Docker chưa sẵn sàng: {status['reason']} "
                "Hệ thống TỪ CHỐI chạy mã do AI sinh ra trực tiếp trên máy thật. "
                f"Cách xử lý: bật Docker rồi chạy `docker build -t {DOCKER_IMAGE} codebase/sandbox`. "
                "Nếu bạn hiểu rủi ro và vẫn muốn chạy trên máy thật, "
                "đặt VLEARN_UNSAFE_HOST_TESTS=1 trong .env."
            ),
        }

    return _run_on_host(files, status['reason'])


def _run_in_docker(files):
    workdir = tempfile.mkdtemp(prefix="vlearn_sandbox_")
    try:
        _write_repo(files, workdir)
    except Exception as e:
        shutil.rmtree(workdir, ignore_errors=True)
        return {"ran": False, "sandbox": "docker", "reason": f"Không ghi được repo: {e}"}

    cmd = [
        'docker', 'run', '--rm',
        '--network', 'none',
        '--read-only',
        '--tmpfs', '/tmp:rw,noexec,nosuid,size=64m',
        '--memory', SANDBOX_MEMORY,
        '--cpus', SANDBOX_CPUS,
        '--pids-limit', str(SANDBOX_PIDS_LIMIT),
        '--cap-drop', 'ALL',
        '--security-opt', 'no-new-privileges',
        '-v', f'{workdir}:/work:rw',
        '-w', '/work',
        '-e', 'PYTHONDONTWRITEBYTECODE=1',
        '-e', 'PYTHONIOENCODING=utf-8',
        DOCKER_IMAGE,
        'python', '-m', 'pytest', '-v', '--no-header', '-p', 'no:cacheprovider',
    ]

    try:
        proc = _run(cmd, timeout=TEST_RUN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        # `docker run` bị giết nhưng container có thể còn sống — dọn cho sạch.
        _kill_stray_containers()
        return {
            "ran": True, "sandbox": "docker", "timedOut": True,
            "passed": 0, "failed": 0, "total": 0, "returncode": -1, "cases": [],
            "command": 'docker run … pytest -v',
            "output": f"Quá {TEST_RUN_TIMEOUT_SECONDS} giây chưa xong — nghi có vòng lặp vô hạn.",
            "fullOutput": f"Quá {TEST_RUN_TIMEOUT_SECONDS} giây chưa xong — nghi có vòng lặp vô hạn.",
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    report = _parse_pytest_output(
        (proc.stdout or '') + (proc.stderr or ''), proc.returncode,
        'docker run --network none --read-only --cap-drop ALL … python -m pytest -v',
    )
    report['sandbox'] = 'docker'
    return report


def _kill_stray_containers():
    """Dọn container còn sót sau khi `docker run` bị timeout."""
    try:
        listed = _run(['docker', 'ps', '-q', '--filter', f'ancestor={DOCKER_IMAGE}'], timeout=15)
        for cid in (listed.stdout or '').split():
            _run(['docker', 'kill', cid], timeout=15)
    except Exception:
        pass


def _run_on_host(files, why):
    """Lối thoát hiểm khi không có Docker — CHỈ chạy khi người dùng tự bật.

    Kém an toàn hơn hẳn: chỉ còn quét tĩnh của security.py bảo vệ. Báo cáo trả
    về luôn gắn cờ để Coach biết bài này chưa được kiểm trong sandbox thật.
    """
    workdir = tempfile.mkdtemp(prefix="vlearn_hosttest_")
    try:
        _write_repo(files, workdir)
        env = {
            'PATH': os.environ.get('PATH', ''),
            'HOME': workdir,
            'PYTHONDONTWRITEBYTECODE': '1',
            'PYTHONIOENCODING': 'utf-8',
        }
        proc = subprocess.Popen(
            [sys.executable, '-m', 'pytest', '-v', '--no-header', '-p', 'no:cacheprovider'],
            cwd=workdir, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, errors='replace', start_new_session=True,
        )
        try:
            output = proc.communicate(timeout=TEST_RUN_TIMEOUT_SECONDS)[0]
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), 9)
            except Exception:
                proc.kill()
            proc.communicate()
            return {
                "ran": True, "sandbox": "host-unsafe", "timedOut": True,
                "passed": 0, "failed": 0, "total": 0, "returncode": -1, "cases": [],
                "command": f'{sys.executable} -m pytest -v',
                "output": f"Quá {TEST_RUN_TIMEOUT_SECONDS} giây chưa xong — nghi có vòng lặp vô hạn.",
                "fullOutput": f"Quá {TEST_RUN_TIMEOUT_SECONDS} giây chưa xong.",
            }

        report = _parse_pytest_output(output, proc.returncode, f'{sys.executable} -m pytest -v')
        report['sandbox'] = 'host-unsafe'
        report['sandboxWarning'] = (
            f"⚠️ Chạy TRỰC TIẾP trên máy thật, không có Docker cách ly ({why}). "
            "Chỉ còn quét tĩnh bảo vệ."
        )
        return report
    except Exception as e:
        return {"ran": False, "sandbox": "host-unsafe", "reason": f"Không chạy được test: {e}"}
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
