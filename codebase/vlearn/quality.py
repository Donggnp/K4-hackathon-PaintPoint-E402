"""Đo chất lượng bài học bằng máy: toàn vẹn, mật độ giải thích, thời lượng.

Đây là nơi các ràng buộc của lớp trở thành con số kiểm chứng được, thay vì lời
hứa trong prompt.
"""

import math
import re

from .config import (
    CHARS_PER_EXPLANATION_LINE,
    LINES_PER_MINUTE,
    MAX_LOGIC_LINES,
    MAX_PHASES,
    MAX_REPO_FILES,
    MIN_EXPLANATION_RATIO,
    MIN_LOGIC_LINES,
    MIN_PHASES,
    MIN_REPO_FILES,
    READ_MINUTES_PER_PHASE,
    VERIFY_MINUTES_PER_PHASE,
)
from .packaging import count_logic_lines



# ---------------------------------------------------------------------------
# Chốt chặn chất lượng
# ---------------------------------------------------------------------------
def verify_tutorial_matches_repo(repo_files, steps, starter_kit):
    """QUY TẮC CỨNG: làm theo tutorial phải ra ĐÚNG repo đã duyệt, không sai một ký tự.

    Trả về danh sách vấn đề (rỗng nghĩa là đạt). Đây là thứ khiến app này dùng
    được trong lớp thật: nếu tutorial trôi khỏi repo, học viên sẽ gõ theo rồi
    thấy test đỏ mà không hiểu vì sao — lỗi tệ nhất một app giáo dục có thể mắc.
    """
    by_path = {f['path']: (f.get('content') or '') for f in repo_files}
    kit = set(starter_kit or [])
    problems = []
    covered = set()

    for step in steps or []:
        for block in step.get('blocks') or []:
            if block.get('type') != 'code' or not block.get('filename'):
                continue
            path = block['filename']
            if path not in by_path:
                problems.append(f"Bước {step.get('num')}: tutorial dạy file '{path}' nhưng repo không có file này.")
                continue
            # Đã được tutorial nhắc tới thì coi là "có dạy", kể cả khi nội dung còn
            # lệch — nếu không sẽ báo thêm lỗi "chưa dạy file này" gây hiểu nhầm.
            covered.add(path)
            if (block.get('content') or '') != by_path[path]:
                problems.append(f"Bước {step.get('num')}: nội dung '{path}' trong tutorial LỆCH với file trong repo.")

    for path in by_path:
        if path not in covered and path not in kit:
            problems.append(f"File '{path}' có trong repo nhưng không nằm trong bộ khung khởi động lẫn tutorial — học viên sẽ không bao giờ tạo được nó.")

    for path in kit:
        if path not in by_path:
            problems.append(f"Bộ khung khởi động khai file '{path}' nhưng repo không có.")

    return problems


def strip_html(html):
    """Bỏ thẻ HTML, còn lại văn xuôi thuần để đếm được độ dài giải thích."""
    text = re.sub(r'<br\s*/?>', '\n', html or '')
    text = re.sub(r'</(p|li|ul|ol|div)>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ')
    return ' '.join(text.split())


def explanation_lines(html):
    """Quy đổi một đoạn giải thích ra số 'dòng' để so với số dòng code."""
    plain = strip_html(html)
    return math.ceil(len(plain) / CHARS_PER_EXPLANATION_LINE) if plain else 0


def measure_step_balance(step):
    """Đếm số dòng code và số dòng giải thích của một bước.

    Khối 'text' và 'callout' được tính là giải thích (callout thường mang phần
    'bẫy thường gặp' và lý do thiết kế — đó cũng là dạy). Khối 'checklist' và
    'quiz' KHÔNG tính, vì đó là kiểm tra chứ không phải giảng.
    """
    code_lines = 0
    explain_lines = 0

    for block in step.get('blocks') or []:
        kind = block.get('type')
        if kind == 'code' and block.get('filename'):
            code_lines += len((block.get('content') or '').splitlines())
        elif kind in ('text', 'callout'):
            explain_lines += explanation_lines(block.get('content'))

    required = math.ceil(code_lines / MIN_EXPLANATION_RATIO)
    return code_lines, explain_lines, required


def check_explanation_ratio(steps):
    """Bước nào giải thích quá mỏng so với lượng code thì nêu tên ra."""
    problems = []
    for step in steps or []:
        code_lines, explain_lines, required = measure_step_balance(step)
        if code_lines and explain_lines < required:
            problems.append(
                f"Bước {step.get('num')} ({step.get('title', '')[:40]}): {code_lines} dòng code "
                f"nhưng chỉ {explain_lines} dòng giải thích — cần tối thiểu {required} dòng."
            )
    return problems


def estimate_step_minutes(step, repo_files):
    """Ước lượng phút cho một bước theo số dòng học viên phải gõ."""
    by_path = {f['path']: (f.get('content') or '') for f in repo_files}
    lines = 0
    for block in step.get('blocks') or []:
        if block.get('type') == 'code' and block.get('filename'):
            lines += len(by_path.get(block['filename'], block.get('content') or '').splitlines())

    if lines == 0:
        return max(3, int(step.get('estimatedMinutes') or 4))

    typing = lines / LINES_PER_MINUTE
    return max(3, int(math.ceil(typing + READ_MINUTES_PER_PHASE + VERIFY_MINUTES_PER_PHASE)))


def normalize_lab(lab):
    """Tính lại mọi con số hiển thị cho học viên từ dữ liệu THẬT, rồi tự kiểm.

    LLM hay tự khai một con số thời lượng rồi viết nội dung lệch hẳn với nó.
    Số học viên nhìn thấy phải suy ra từ chính lượng code họ phải gõ.
    """
    steps = lab.get('steps') or []
    repo_files = ((lab.get('repo') or {}).get('files')) or []
    starter_kit = lab.get('starterKit') or []

    total = 0
    for i, step in enumerate(steps):
        step['num'] = i                      # Bước 0 là bước tải bộ khung khởi động
        step['estimatedMinutes'] = estimate_step_minutes(step, repo_files)
        total += step['estimatedMinutes']

    if total > 0:
        lab['duration'] = f"{total} phút"

    warnings = []
    if total and not (30 <= total <= 45):
        warnings.append(f"Tổng thời lượng {total} phút nằm ngoài khung 30-45 phút — nên bớt/thêm một phase.")

    phases = max(0, len(steps) - 1)          # trừ Bước 0
    if phases and not (MIN_PHASES <= phases <= MAX_PHASES):
        warnings.append(f"Có {phases} phase (yêu cầu {MIN_PHASES}-{MAX_PHASES}).")

    if repo_files and not (MIN_REPO_FILES <= len(repo_files) <= MAX_REPO_FILES):
        warnings.append(f"Repo có {len(repo_files)} file (yêu cầu {MIN_REPO_FILES}-{MAX_REPO_FILES}).")

    if repo_files:
        loc = count_logic_lines(repo_files, starter_kit)
        lab.setdefault('summary', {})['logicLines'] = loc
        if not (MIN_LOGIC_LINES <= loc <= MAX_LOGIC_LINES):
            warnings.append(f"Học viên phải gõ {loc} dòng logic (yêu cầu {MIN_LOGIC_LINES}-{MAX_LOGIC_LINES}).")

    report = lab.get('testReport') or {}
    if report.get('ran') and report.get('returncode') not in (0, None):
        warnings.append(
            f"Repo KHÔNG pass hết test: {report.get('passed', 0)}/{report.get('total', 0)} "
            f"— không được duyệt cho tới khi xanh hết."
        )

    flagged = lab.get('generatedFromFailingTests')
    if flagged:
        warnings.append(
            f"Tutorial này được sinh khi repo còn test ĐỎ "
            f"({flagged.get('passed', 0)}/{flagged.get('total', 0)}) — Lab Coach đã xác nhận "
            f"chấp nhận. Hãy sửa repo cho xanh trước khi phát hành cho học viên."
        )

    thin = check_explanation_ratio(steps)
    if thin:
        lab['explanationProblems'] = thin
        warnings.append(
            f"Giải thích quá mỏng ở {len(thin)} bước (luật: mỗi 4 dòng code cần ≥1 dòng giải thích)."
        )
    else:
        lab['explanationProblems'] = []

    if steps and repo_files:
        mismatches = verify_tutorial_matches_repo(repo_files, steps, starter_kit)
        if mismatches:
            lab['integrityProblems'] = mismatches
            warnings.append(f"NGHIÊM TRỌNG: tutorial không khớp repo ở {len(mismatches)} chỗ — làm theo sẽ KHÔNG ra đúng repo.")
        else:
            lab['integrityProblems'] = []

    lab['qualityWarnings'] = warnings
    return lab
