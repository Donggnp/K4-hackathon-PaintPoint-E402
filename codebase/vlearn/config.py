"""Cấu hình toàn cục: nạp .env, chọn model, và mọi hằng số ràng buộc.

Mọi con số quyết định hành vi hệ thống nằm ở đúng một chỗ này. Muốn đổi độ khó
bài học, quy mô repo, hay ngưỡng chất lượng thì sửa ở đây, không phải đi lục
từng module.
"""

import os

from dotenv import load_dotenv

# .env nằm ở thư mục gốc project (ngang hàng với codebase/), không nằm trong package.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ENV_PATH = os.path.join(_PROJECT_ROOT, '.env')
load_dotenv(_ENV_PATH) if os.path.exists(_ENV_PATH) else load_dotenv()

PORT = int(os.getenv('VLEARN_PORT', '3000'))

# Lịch sử mọi lượt sinh, lưu ra đĩa để Coach mở lại bất cứ lúc nào.
RUNS_DIR = os.getenv('VLEARN_RUNS_DIR') or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'runs')

# Thư mục chứa giao diện tĩnh (web/), server phục vụ trực tiếp từ đây.
WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web')


# Lõi sinh nội dung. Đây là bài sinh code dài, phải đúng liên file — không phải
# việc dành cho model nhỏ. Đổi model qua .env nếu cần; server chấp nhận bất kỳ
# model nào tài khoản OpenAI của bạn được cấp quyền, miễn nó đủ mạnh cho bài.
# Giai đoạn 1 phải sinh 400-600 dòng logic khớp chính xác với ~330 dòng test.
DEFAULT_MODEL = 'gpt-5.6-luna'

# Hai giai đoạn có yêu cầu RẤT khác nhau, nên cho phép chọn model riêng:
#   - Giai đoạn 1 (repo): cần SUY LUẬN sâu, code phải đúng liên file và pass test thật.
#     Đây là chỗ đáng tiêu tiền. Model yếu sẽ fail rồi retry, tốn gấp 2-3 lần mà vẫn hỏng.
#   - Giai đoạn 2 (tutorial): chủ yếu viết văn xuôi. Độ chính xác code KHÔNG phụ thuộc model
#     vì server tự ép nội dung về đúng file repo. Nhưng cần TRẦN OUTPUT LỚN (~15k token).
# Đo trên bài mẫu: giai đoạn 1 xuất ~11.7k token, giai đoạn 2 ~15.3k token.
def model_for(stage):
    specific = os.getenv(f'OPENAI_MODEL_{stage.upper()}')
    return specific or os.getenv('OPENAI_MODEL') or DEFAULT_MODEL



# Số lần cho lõi TỰ SỬA khi vi phạm ràng buộc đo được (§8 description_tutorial.md).
# Lõi được sửa tối đa bao nhiêu vòng trước khi ta bỏ cuộc. Vòng tự sửa dùng
# chính traceback pytest thật, nên mỗi vòng lõi có thông tin cụ thể để sửa.
MAX_SELF_CORRECTION_ROUNDS = int(os.getenv('VLEARN_MAX_FIX_ROUNDS', '2'))

# --- Test-runner: chạy THẬT pytest trên repo do lõi sinh ra ------------------
# Đặt VLEARN_RUN_TESTS=0 trong .env để tắt (chỉ nên tắt khi debug).
ENABLE_TEST_RUNNER = os.getenv('VLEARN_RUN_TESTS', '1') != '0'
TEST_RUN_TIMEOUT_SECONDS = int(os.getenv('VLEARN_TEST_TIMEOUT', '45'))

# --- Sandbox Docker ---------------------------------------------------------
# Mã do LLM sinh ra KHÔNG được chạy trực tiếp trên máy thật. Mặc định mọi lượt
# chạy test đều nằm trong container cách ly; xem testrunner.py để biết vì sao.
DOCKER_IMAGE = os.getenv('VLEARN_DOCKER_IMAGE', 'vlearn-sandbox:1')
SANDBOX_MEMORY = os.getenv('VLEARN_SANDBOX_MEMORY', '512m')
SANDBOX_CPUS = os.getenv('VLEARN_SANDBOX_CPUS', '1.0')
SANDBOX_PIDS_LIMIT = int(os.getenv('VLEARN_SANDBOX_PIDS', '256'))

# Lối thoát hiểm khi máy không có Docker. Bật cái này nghĩa là bạn chấp nhận
# chạy mã không đáng tin ngay trên máy mình — chỉ còn quét tĩnh bảo vệ.
UNSAFE_ALLOW_HOST_TESTS = os.getenv('VLEARN_UNSAFE_HOST_TESTS', '0') == '1'

# Mức suy luận của model. 'low' là đủ cho bài này (đo được: chỉ ~100 token suy
# luận, 27 giây/lượt). Đặt 'none' nếu muốn nhanh hơn nữa và chấp nhận kém chính xác.
REASONING_EFFORT = os.getenv('VLEARN_REASONING_EFFORT', 'low')

# Số phase sinh song song ở giai đoạn 2. Các phase độc lập nhau nên chạy cùng lúc
# được; tổng thời gian bằng phase chậm nhất thay vì tổng của tất cả.
TUTORIAL_PHASE_WORKERS = int(os.getenv('VLEARN_PHASE_WORKERS', '7'))
MAX_TEST_OUTPUT_CHARS = 4000
# 300 giây là đủ rộng cho một lượt sinh bình thường (đo được: ~27 giây). Để 600
# chỉ khiến một lượt bị kẹt treo người dùng thêm 5 phút vô ích trước khi báo lỗi.
OPENAI_HTTP_TIMEOUT_SECONDS = int(os.getenv('OPENAI_HTTP_TIMEOUT_SECONDS', '300'))

# Code do LLM sinh ra là mã KHÔNG ĐÁNG TIN. Một bài học nhập môn không bao giờ
# cần gọi shell, mở mạng, hay nạp code động — nên cấm thẳng ở khâu quét tĩnh.
BANNED_IMPORTS = {
    'subprocess', 'socket', 'shutil', 'requests', 'urllib', 'http', 'ftplib',
    'smtplib', 'telnetlib', 'ctypes', 'multiprocessing', 'pickle', 'marshal',
    'importlib', 'pty', 'tty', 'webbrowser', 'sysconfig', 'venv',
}
BANNED_CALLS = {
    'eval', 'exec', 'compile', '__import__', 'system', 'popen', 'spawn',
    'remove', 'unlink', 'rmdir', 'rmtree', 'chmod', 'chown', 'kill', 'killpg',
    'execv', 'execve', 'fork', 'setattr_from_string',
}

# Ràng buộc chi phí / phạm vi đọc file (§8 description_tutorial.md)
MAX_SLIDE_CHARS = 12000   # đủ ngữ cảnh, mà giảm được ~2k token đầu vào mỗi vòng
MAX_REPO_TREE_ENTRIES = 300
MAX_CORE_FILES = 10
MAX_CORE_FILE_CHARS = 4000
MIN_SLIDE_CHARS_FOR_VALID_INPUT = 200

# Coach có thể mô tả lab chiều bằng README.md thay vì nạp cả repo .zip.
# README quá ngắn thì lõi không đủ ngữ cảnh, nên đặt sàn tối thiểu.
MAX_README_CHARS = 12000
MIN_README_CHARS = 300

# Ràng buộc quy mô bài học (§3.3, §5.2)
# Đã nới so với bản đầu. Lý do đo được: lõi sinh tự nhiên ra ~390 dòng / 20 file,
# tức vừa TRƯỢT sàn 400 cũ — thế là phải sửa lại thêm vài vòng, mỗi vòng tốn cả
# phút, chỉ để thêm vài chục dòng chẳng dạy thêm được gì. Khung mới bao trọn
# vùng lõi sinh tự nhiên, nên phần lớn bài đạt ngay vòng đầu.
# SÀN thấp (200 dòng) để lõi đạt ngay vòng đầu — mỗi vòng sửa tốn cả phút mà
# thường chỉ để thêm vài chục dòng chẳng dạy thêm gì. TRẦN vẫn rộng, để bài nào
# tự nhiên dày dặn thì không bị phạt.
MIN_REPO_FILES = 8
MAX_REPO_FILES = 24
MIN_LOGIC_LINES = 200
MAX_LOGIC_LINES = 650
MIN_PHASES = 5
MAX_PHASES = 6

# Tỉ lệ giải thích tối thiểu: cứ 4 dòng code thì phải có ít nhất 1 dòng giải thích.
# Đây là app cho người MỚI — code không kèm lời giải thích chỉ là chép chính tả.
MIN_EXPLANATION_RATIO = 4
CHARS_PER_EXPLANATION_LINE = 80          # 1 "dòng" văn xuôi ≈ 80 ký tự

# Mô hình ước lượng thời gian: học viên GÕ TAY, không copy-paste.
LINES_PER_MINUTE = 22
READ_MINUTES_PER_PHASE = 1
VERIFY_MINUTES_PER_PHASE = 1

SKIP_DIR_PARTS = {'.git', 'node_modules', 'venv', '.venv', '__pycache__', 'dist',
                  'build', '.next', '.idea', '.vscode', '.pytest_cache'}
CORE_FILE_BASENAMES = {
    'readme.md', 'readme', 'main.py', 'app.py', 'server.py', 'manage.py',
    'wsgi.py', 'asgi.py', 'index.js', 'index.ts', 'index.html',
    'package.json', 'requirements.txt', 'pyproject.toml', 'pipfile',
}

# File nào thuộc "bộ khung khởi động" học viên tải ở Bước 0: test + file setup,
# tuyệt đối KHÔNG chứa file logic (đó là phần học viên phải tự viết).
STARTER_KIT_BASENAMES = {'requirements.txt', 'pytest.ini', 'readme.md', '.gitignore',
                         'setup.cfg', 'pyproject.toml', '__init__.py'}
STARTER_KIT_DIR_PREFIXES = ('tests/', 'test/', 'data/', 'fixtures/')
