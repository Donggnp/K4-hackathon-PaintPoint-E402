"""Đọc đầu vào của Lab Coach: slide PDF, repo .zip, hoặc README.md.

Nguyên tắc: mọi nội dung đọc từ đây là DỮ LIỆU, không phải chỉ thị. Chúng được
nhét vào prompt như tài liệu tham khảo, và prompt đã dặn lõi bỏ qua mọi câu
kiểu "ignore previous instructions" nằm trong đó.
"""

import io
import zipfile

from .config import (
    CORE_FILE_BASENAMES,
    MAX_CORE_FILE_CHARS,
    MAX_CORE_FILES,
    MAX_REPO_TREE_ENTRIES,
    MAX_README_CHARS,
    MAX_SLIDE_CHARS,
    SKIP_DIR_PARTS,
)

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None



# ---------------------------------------------------------------------------
# Trích xuất đầu vào
# ---------------------------------------------------------------------------
def extract_pdf_text(pdf_bytes):
    """Đọc text thật từ PDF theo từng trang, giữ số trang gốc để trích dẫn."""
    if PdfReader is None:
        raise RuntimeError("Thiếu thư viện pypdf — chạy: pip install -r requirements.txt")

    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []
    total_chars = 0
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        if total_chars + len(text) > MAX_SLIDE_CHARS:
            remaining = max(0, MAX_SLIDE_CHARS - total_chars)
            text = text[:remaining] + ("\n[...cắt bớt do vượt giới hạn chi phí...]" if remaining else "")
        pages.append((i, text))
        total_chars += len(text)
        if total_chars >= MAX_SLIDE_CHARS:
            break

    block = "\n\n".join(f"--- Slide Trang {n} ---\n{t}" for n, t in pages)
    return block, len(pages), len(reader.pages)


def extract_repo_summary(zip_bytes):
    """Đọc file tree + nội dung file cốt lõi từ ZIP repo lab chiều."""
    file_tree = []
    core_files = []

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for info in zf.infolist():
            name = info.filename
            if name.endswith('/'):
                continue
            parts = name.split('/')
            if any(p in SKIP_DIR_PARTS for p in parts):
                continue

            if len(file_tree) < MAX_REPO_TREE_ENTRIES:
                file_tree.append(name)

            basename = parts[-1].lower()
            if basename in CORE_FILE_BASENAMES and len(core_files) < MAX_CORE_FILES:
                try:
                    content = zf.read(info).decode('utf-8', errors='ignore')
                except Exception:
                    content = ""
                if content:
                    if len(content) > MAX_CORE_FILE_CHARS:
                        content = content[:MAX_CORE_FILE_CHARS] + "\n[...cắt bớt do vượt giới hạn chi phí...]"
                    core_files.append((name, content))

    tree_block = "\n".join(f"- {p}" for p in file_tree)
    core_block = "\n\n".join(f"### File cốt lõi: {p}\n```\n{c}\n```" for p, c in core_files)
    block = f"File tree ({len(file_tree)} file):\n{tree_block}\n\nNội dung file cốt lõi:\n{core_block}"
    return block, file_tree, [p for p, _ in core_files]


def extract_readme_summary(text, filename='README.md'):
    """Đọc README.md của lab buổi chiều thay cho cả repo .zip.

    Vì sao cho phép cách này? Zip cả repo có thể vài chục MB, trong khi thứ lõi
    thật sự cần chỉ là: lab chiều LÀM GÌ, dùng công nghệ gì, kiến trúc ra sao.
    README tốt trả lời đủ cả ba, mà nhẹ hơn hàng trăm lần.

    Trả về (khối text đã cắt theo hạn mức, nhãn nguồn để ghi vào prompt).
    """
    content = (text or '').strip()

    if len(content) > MAX_README_CHARS:
        content = content[:MAX_README_CHARS] + "\n[...cắt bớt do vượt giới hạn chi phí...]"

    block = (
        "Coach chỉ cung cấp README.md của repo lab chiều (không nạp toàn bộ mã nguồn).\n"
        "Hãy dựa vào mô tả dưới đây để nắm domain, công nghệ và kiến trúc của lab chiều.\n\n"
        f"{content}"
    )
    return block, filename
