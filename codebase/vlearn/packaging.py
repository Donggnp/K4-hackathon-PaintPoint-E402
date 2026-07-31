"""Đóng gói / mở gói repo, và tách bộ khung khởi động cho Bước 0.

Coach tải repo về sửa bằng IDE rồi upload ngược lên; học viên tải bộ khung
khởi động. Cả hai đi qua đúng hai hàm ở đây.
"""

import base64
import io
import os
import zipfile

from .config import SKIP_DIR_PARTS, STARTER_KIT_BASENAMES, STARTER_KIT_DIR_PREFIXES



# ---------------------------------------------------------------------------
# Đóng gói / mở gói repo (Coach tải về sửa bằng IDE rồi upload ngược lại)
# ---------------------------------------------------------------------------
def files_to_zip_base64(files, root_name):
    """[{path, content}] -> chuỗi base64 của file .zip."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item in files:
            path = (item.get('path') or '').lstrip('/')
            if not path:
                continue
            zf.writestr(f"{root_name}/{path}", item.get('content') or '')
    return base64.b64encode(buffer.getvalue()).decode('ascii')


def zip_base64_to_files(zip_b64):
    """Chuỗi base64 của .zip -> [{path, content}], đã bỏ thư mục gốc thừa và file rác."""
    raw = base64.b64decode(zip_b64)
    entries = []

    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = []
        for info in zf.infolist():
            if info.filename.endswith('/'):
                continue
            parts = info.filename.split('/')
            if any(p in SKIP_DIR_PARTS for p in parts):
                continue
            if parts[-1].endswith('.pyc') or parts[-1] == '.DS_Store':
                continue
            names.append(info)

        # Nếu mọi file đều nằm dưới cùng một thư mục gốc, bỏ thư mục đó đi.
        tops = {n.filename.split('/')[0] for n in names if '/' in n.filename}
        strip_root = len(tops) == 1 and all('/' in n.filename for n in names)
        root = tops.pop() if strip_root else None

        for info in names:
            path = info.filename[len(root) + 1:] if strip_root else info.filename
            if not path:
                continue
            try:
                content = zf.read(info).decode('utf-8')
            except UnicodeDecodeError:
                # File nhị phân không sửa được trên web -> bỏ qua, báo cho Coach biết.
                continue
            entries.append({"path": path, "content": content})

    entries.sort(key=lambda e: e['path'])
    return entries


def is_starter_kit_file(path):
    """File này có thuộc bộ khung khởi động học viên tải ở Bước 0 không?"""
    normalized = path.lower()
    if normalized.startswith(STARTER_KIT_DIR_PREFIXES):
        return True
    return os.path.basename(normalized) in STARTER_KIT_BASENAMES


def derive_starter_kit(files):
    """Suy ra danh sách file cho Bước 0 từ toàn bộ repo."""
    return [f['path'] for f in files if is_starter_kit_file(f['path'])]


def logic_files(files, starter_kit):
    """Các file học viên phải TỰ VIẾT (không nằm trong bộ khung khởi động)."""
    kit = set(starter_kit)
    return [f for f in files if f['path'] not in kit]


def count_logic_lines(files, starter_kit):
    return sum(len((f.get('content') or '').splitlines()) for f in logic_files(files, starter_kit))
