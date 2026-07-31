"""Quét tĩnh code do lõi sinh ra, TRƯỚC khi cho phép chạy.

Chỉ đọc cây cú pháp bằng `ast`, không thực thi dòng nào. Đây là phòng thủ nhiều
lớp, KHÔNG phải sandbox thật — xem README phần Test-runner.
"""

import ast

from .config import BANNED_CALLS, BANNED_IMPORTS



def security_scan(files):
    """Quét TĨNH code do lõi sinh ra TRƯỚC khi cho chạy (§6.2, §6.3).

    Đây là mã không đáng tin: nó do một mô hình ngôn ngữ viết ra từ nội dung
    slide và repo mà người ngoài nạp lên. Ta phân tích bằng `ast` — chỉ đọc cây
    cú pháp, KHÔNG thực thi — để chặn những thứ một bài học không bao giờ cần:
    gọi shell, xoá file, mở mạng, hay nạp code động.

    Nói rõ giới hạn: đây là phòng thủ nhiều lớp, KHÔNG phải sandbox thật. Muốn
    an toàn tuyệt đối phải chạy trong container/VM riêng.
    """
    problems = []

    for f in files:
        path = f.get('path') or ''
        if not path.endswith('.py'):
            continue

        try:
            tree = ast.parse(f.get('content') or '')
        except SyntaxError:
            continue                      # lỗi cú pháp đã có audit_repo báo riêng

        for node in ast.walk(tree):
            # import các module không được phép
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split('.')[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or '').split('.')[0]]

            for name in names:
                if name in BANNED_IMPORTS:
                    problems.append(
                        f"BẢO MẬT — '{path}' import '{name}'. Bài học không được gọi shell/mạng/tiến trình. "
                        f"Hãy viết lại chỉ dùng thư viện chuẩn an toàn."
                    )

            # gọi hàm nguy hiểm
            if isinstance(node, ast.Call):
                fname = ''
                if isinstance(node.func, ast.Name):
                    fname = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    fname = node.func.attr

                if fname in BANNED_CALLS:
                    problems.append(
                        f"BẢO MẬT — '{path}' gọi '{fname}()'. Tuyệt đối không nạp code động, "
                        f"xoá file hay chạy lệnh hệ thống. Hãy viết lại."
                    )

                # open(...) ở chế độ ghi
                if fname == 'open' and len(node.args) >= 2:
                    mode = node.args[1]
                    if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
                        if any(c in mode.value for c in 'wax+'):
                            problems.append(
                                f"BẢO MẬT — '{path}' mở file ở chế độ ghi ('{mode.value}'). "
                                f"Mini-lab chỉ được ĐỌC dữ liệu, không ghi ra đĩa."
                            )

    # bỏ trùng, giữ nguyên thứ tự
    seen = set()
    unique = []
    for p in problems:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique
