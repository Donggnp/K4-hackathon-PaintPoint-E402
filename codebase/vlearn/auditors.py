"""Chấm bài của lõi bằng tiêu chí ĐO ĐƯỢC, rồi trả lỗi ngược lại cho nó sửa.

Prompt chỉ là lời dặn. Hai hàm ở đây mới là thứ ép lõi tuân thủ.
"""

import ast
import os
import re

from .config import (
    MAX_LOGIC_LINES,
    MAX_PHASES,
    MAX_REPO_FILES,
    MIN_LOGIC_LINES,
    MIN_PHASES,
    MIN_REPO_FILES,
)
from .packaging import count_logic_lines, derive_starter_kit
from .quality import check_explanation_ratio, verify_tutorial_matches_repo
from .security import security_scan
from .testrunner import run_repo_tests



def audit_repo(lab):
    """Chấm bài GIAI ĐOẠN 1 của lõi bằng các tiêu chí ĐO ĐƯỢC.

    Trả về danh sách vi phạm bằng tiếng Việt, viết ở dạng RA LỆNH SỬA để đưa
    thẳng lại cho model ở vòng sau. Rỗng nghĩa là đạt.
    """
    problems = []
    files = ((lab.get('repo') or {}).get('files')) or []
    paths = [f.get('path') or '' for f in files]

    if not (MIN_REPO_FILES <= len(files) <= MAX_REPO_FILES):
        problems.append(
            f"Repo đang có {len(files)} file, yêu cầu {MIN_REPO_FILES}-{MAX_REPO_FILES}. "
            f"Hãy {'thêm' if len(files) < MIN_REPO_FILES else 'gộp bớt'} module cho đúng khung."
        )

    starter = derive_starter_kit(files)
    loc = count_logic_lines(files, starter)
    if not (MIN_LOGIC_LINES <= loc <= MAX_LOGIC_LINES):
        problems.append(
            f"Chỉ có {loc} dòng logic (không tính test và file setup), yêu cầu "
            f"{MIN_LOGIC_LINES}-{MAX_LOGIC_LINES}. Hãy "
            f"{'viết thêm module thật, KHÔNG độn comment' if loc < MIN_LOGIC_LINES else 'rút gọn'}."
        )

    # Kiểm cú pháp Python bằng ast — chỉ PHÂN TÍCH, không thực thi dòng nào.
    for f in files:
        path = f.get('path') or ''
        if not path.endswith('.py'):
            continue
        try:
            ast.parse(f.get('content') or '')
        except SyntaxError as e:
            problems.append(f"File '{path}' sai cú pháp Python ở dòng {e.lineno}: {e.msg}. Hãy viết lại file này cho đúng.")

    if not any(p.startswith('tests/') for p in paths):
        problems.append("Thiếu thư mục tests/. Bắt buộc phải có bộ test tự động.")
    if 'requirements.txt' not in paths:
        problems.append("Thiếu requirements.txt.")
    if 'pytest.ini' not in paths:
        problems.append("Thiếu pytest.ini (phải có `pythonpath = .` để test import được package).")
    if not any(p.startswith('src/') for p in paths):
        problems.append("Thiếu thư mục src/. Code logic phải chia module trong src/, không để hết ở gốc.")

    depth = max((p.count('/') for p in paths), default=0)
    if depth < 2:
        problems.append("Cấu trúc quá phẳng. Cần ít nhất một package con lồng nhau kiểu src/<package>/<module>.py.")

    # Chỉ bắt dấu hiệu VIỆC CHƯA LÀM XONG. Lưu ý: `raise NotImplementedError`
    # trong lớp cha là mẫu thiết kế ĐÚNG (ép lớp con phải cài đè), nên KHÔNG
    # tính là lỗi — bắt nhầm nó sẽ đuổi model khỏi một kiến trúc tốt.
    for f in files:
        path = f.get('path') or ''
        if path.startswith('tests/'):
            continue
        content = f.get('content') or ''
        if re.search(r'\b(TODO|FIXME|XXX)\b', content):
            problems.append(
                f"File '{path}' còn ghi chú TODO/FIXME. Repo này là ĐÁP ÁN CHUẨN, phải hoàn chỉnh."
            )
            break

    # --- Lỗi kinh điển của LLM: bắt SỚM để phản hồi cho lõi rõ ràng hơn
    #     nhiều so với việc để pytest nổ ra một đống ImportError khó đọc. ---
    path_set = set(paths)

    # 1. Thư mục package thiếu __init__.py -> import chết ngay
    pkg_dirs = {os.path.dirname(p) for p in paths if p.endswith('.py') and '/' in p}
    for d in sorted(pkg_dirs):
        if not d:
            continue
        if f"{d}/__init__.py" not in path_set:
            problems.append(
                f"Thư mục '{d}/' có file .py nhưng thiếu '{d}/__init__.py'. "
                f"Thiếu file này thì mọi import từ package đó sẽ hỏng."
            )

    # 2. Test import module không tồn tại
    for f in files:
        fp = f.get('path') or ''
        if not fp.startswith('tests/') or not fp.endswith('.py'):
            continue
        try:
            tree = ast.parse(f.get('content') or '')
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            mod = None
            if isinstance(node, ast.ImportFrom) and node.level == 0:
                mod = node.module or ''
            elif isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.split('.')[0] in ('src', 'config'):
                        mod = a.name
            if not mod or mod.split('.')[0] not in ('src', 'config'):
                continue
            as_module = mod.replace('.', '/') + '.py'
            as_package = mod.replace('.', '/') + '/__init__.py'
            if as_module not in path_set and as_package not in path_set:
                problems.append(
                    f"'{fp}' import '{mod}' nhưng repo không có file '{as_module}'. "
                    f"Hãy tạo file đó, hoặc sửa lại đường dẫn import cho khớp cây thư mục."
                )

    # 3. Nguồn ngẫu nhiên/thời gian -> test sẽ lúc xanh lúc đỏ
    for f in files:
        fp = f.get('path') or ''
        if not fp.endswith('.py'):
            continue
        content = f.get('content') or ''
        for bad, why in (('random.', 'số ngẫu nhiên'),
                         ('datetime.now', 'thời gian hiện tại'),
                         ('time.time', 'thời gian hiện tại'),
                         ('uuid.', 'uuid ngẫu nhiên')):
            if bad in content:
                problems.append(
                    f"'{fp}' dùng {bad} ({why}). Bài học phải TẤT ĐỊNH — cùng đầu vào luôn cho "
                    f"cùng đầu ra, nếu không test sẽ lúc xanh lúc đỏ. Hãy bỏ nguồn không tất định này."
                )
                break

    # bỏ trùng, giữ thứ tự
    seen_p = set()
    deduped = []
    for x in problems:
        if x not in seen_p:
            seen_p.add(x)
            deduped.append(x)
    problems = deduped

    # Quét bảo mật TRƯỚC khi chạy. Có vi phạm thì tuyệt đối không thực thi.
    security = security_scan(files)
    if security:
        problems.extend(security)
        lab['testReport'] = {
            "ran": False,
            "reason": "Không chạy test vì code còn vi phạm bảo mật — không thực thi mã không an toàn.",
        }
        return problems

    # Chỉ bỏ chạy test khi repo hỏng tới mức pytest không khởi động nổi (sai cú
    # pháp, thiếu tests/, import trỏ vào file không có). Còn lỗi QUY MÔ như thiếu
    # vài chục dòng thì test vẫn chạy được — và PHẢI chạy, vì Coach cần bằng
    # chứng, còn lõi cần biết code mình có đúng hành vi hay không.
    FATAL_MARKERS = ('sai cú pháp', 'Thiếu thư mục tests/', 'Thiếu pytest.ini',
                     'nhưng repo không có file', 'Thiếu requirements.txt')
    fatal = [p for p in problems if any(k in p for k in FATAL_MARKERS)]
    if fatal:
        lab['testReport'] = {
            "ran": False,
            "reason": "Chưa chạy được test vì repo còn lỗi khiến pytest không khởi động nổi: "
                      + fatal[0],
        }
        return problems

    report = run_repo_tests(files)
    lab['testReport'] = report

    if report.get('ran'):
        if report.get('timedOut'):
            problems.append(
                "Chạy `pytest` bị treo quá 60 giây — nghi có vòng lặp vô hạn. "
                "Hãy rà lại các vòng lặp và bảo đảm chúng đều có điều kiện dừng."
            )
        elif report.get('returncode') != 0:
            problems.append(
                f"CHẠY THẬT `pytest` THẤT BẠI: {report.get('passed', 0)} pass, "
                f"{report.get('failed', 0)} fail. Repo BẮT BUỘC phải pass 100% test do chính bạn viết.\n"
                f"Output thật của pytest:\n{report.get('output', '')}\n"
                f"Hãy sửa code logic (hoặc sửa test nếu test sai) rồi trả lại toàn bộ JSON."
            )
        elif report.get('passed', 0) == 0:
            problems.append(
                "`pytest` chạy xong nhưng KHÔNG có test nào được thu thập. "
                "Kiểm tra `pytest.ini` có `pythonpath = .` và các file test đặt đúng trong tests/."
            )

    return problems


def audit_tutorial(lab):
    """Chấm bài GIAI ĐOẠN 2 của lõi bằng các tiêu chí ĐO ĐƯỢC."""
    problems = []
    steps = lab.get('steps') or []
    files = ((lab.get('repo') or {}).get('files')) or []
    starter = lab.get('starterKit') or derive_starter_kit(files)

    if not steps or steps[0].get('num') != 0:
        problems.append("Thiếu Bước 0 (num=0) hướng dẫn tải bộ khung khởi động và dựng môi trường.")

    phases = max(0, len(steps) - 1)
    if not (MIN_PHASES <= phases <= MAX_PHASES):
        problems.append(f"Đang có {phases} phase (chưa kể Bước 0), yêu cầu {MIN_PHASES}-{MAX_PHASES}.")

    # Bước 0 không được chứa file logic.
    if steps and steps[0].get('num') == 0:
        for block in steps[0].get('blocks') or []:
            if block.get('type') == 'code' and block.get('filename') not in (None, ''):
                if block['filename'] not in set(starter):
                    problems.append(
                        f"Bước 0 đang dạy file logic '{block['filename']}'. Bước 0 chỉ được tải bộ khung, không dạy logic."
                    )
                    break

    # Cây thư mục vẽ ở Bước 0 phải khớp bộ khung khởi động THẬT. Học viên đối
    # chiếu thư mục vừa giải nén với hình vẽ này; lệch là họ tưởng mình làm sai.
    for step in steps:
        for block in step.get('blocks') or []:
            if block.get('type') != 'tree':
                continue
            drawn = set()
            for item in block.get('items') or []:
                # Cây thư mục thường vẽ bằng ký tự kẻ khung (├── └── │) và có thể
                # kèm chú thích sau mũi tên. Phải bóc hết mới ra tên file thật.
                name = item.split('←')[0].split('#')[0]
                name = re.sub(r'^[\s│├└─|`\\+-]+', '', name).strip().strip('/')
                if name and '.' in os.path.basename(name):
                    drawn.add(os.path.basename(name))
            if not drawn:
                continue
            real = {os.path.basename(p) for p in starter} if step.get('num') == 0 \
                else {os.path.basename(f['path']) for f in files}
            ghost = drawn - real
            if ghost:
                problems.append(
                    f"Bước {step.get('num')}: cây thư mục vẽ các file không có thật: "
                    f"{', '.join(sorted(ghost))}. Hãy vẽ đúng file có trong repo."
                )

    # Block rỗng render ra một khoảng trắng trên màn hình — học viên thấy bước
    # hướng dẫn thiếu nội dung mà không hiểu vì sao. Phải bắt, không được bỏ qua.
    for step in steps:
        for i, block in enumerate(step.get('blocks') or []):
            kind = block.get('type')
            if kind in ('text', 'callout') and not (block.get('content') or '').strip():
                problems.append(
                    f"Bước {step.get('num')}, khối {i + 1} ({kind}) rỗng — sẽ hiện ra một "
                    f"khoảng trắng trên màn hình. Hãy điền trường 'content'.")
            elif kind in ('tree', 'checklist') and not (block.get('items') or []):
                problems.append(
                    f"Bước {step.get('num')}, khối {i + 1} ({kind}) rỗng — hãy điền trường 'items'.")
            elif kind == 'code' and not (block.get('content') or '').strip() \
                    and not block.get('filename'):
                problems.append(
                    f"Bước {step.get('num')}, khối {i + 1} (code) rỗng và không có tên file.")

    problems.extend(verify_tutorial_matches_repo(files, steps, starter))
    problems.extend(check_explanation_ratio(steps))

    if not any(b.get('type') == 'quiz' for s in steps for b in (s.get('blocks') or [])):
        problems.append("Thiếu câu quiz ở phase cuối.")

    return problems
