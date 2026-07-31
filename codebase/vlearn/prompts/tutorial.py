"""Ví dụ vàng cho GIAI ĐOẠN 2 — một phase thật, đúng nhịp lớp yêu cầu.

Prompt của giai đoạn 2 nằm ở vlearn/tutorial_builder.py, vì tutorial được sinh
theo TỪNG PHASE chạy song song chứ không phải một lượt gọi khổng lồ.
"""

import json

from ..config import MAX_PHASES, MIN_PHASES



# ---------------------------------------------------------------------------
# GIAI ĐOẠN 2 — sinh TUTORIAL từ repo ĐÃ DUYỆT
# ---------------------------------------------------------------------------
# Ví dụ vàng cho tutorial: một phase thật, đúng nhịp giải thích mà lớp yêu cầu.
# Dựng bằng json.dumps từ dict để JSON LUÔN hợp lệ — dạy model bằng mẫu sai cú pháp
# thì nó sẽ chép lại đúng cái sai đó.
_GOLDEN_PHASE_OBJ = {
    "num": 2,
    "title": "Phase 2 — Hợp đồng Tool: chuẩn hoá mọi công cụ",
    "estimatedMinutes": 5,
    "blocks": [
        {
            "type": "text",
            "content": (
                "<p>Đây là phase quan trọng nhất về mặt kiến trúc. Agent sắp có nhiều tool khác nhau. "
                "Nếu tool A trả về <code>dict</code>, tool B trả về chuỗi, tool C ném exception thì vòng lặp "
                "sẽ đầy <code>if/else</code> và vỡ ngay khi bạn thêm tool thứ ba.</p>"
                "<p>Cách chữa là <strong>hợp đồng</strong> (interface) — hiểu đơn giản là bản cam kết: mọi tool "
                "đều hứa trả về cùng một kiểu dữ liệu. Vòng lặp chỉ cần biết bản cam kết đó, không cần biết "
                "ruột từng tool.</p>"
                "<p>Tạo file <code>src/tools/base.py</code>:</p>"
            ),
        },
        {
            "type": "code",
            "lang": "python",
            "filename": "src/tools/base.py",
            "content": "",
        },
        {
            "type": "text",
            "content": (
                "<p><strong>Đọc lại file trên, từng phần:</strong></p><ul>"
                "<li><code>@dataclass</code> — một cách viết tắt của Python. Đặt nó trước lớp thì Python tự sinh "
                "hàm khởi tạo, nên bạn dùng được <code>ToolResult(True, 'xong', 't')</code> ngay. Không có nó "
                "bạn phải tự viết <code>__init__</code> dài dòng.</li>"
                "<li><code>source: str</code> — tool nào tạo ra kết quả này. Lúc chạy tốt thì trường này có vẻ "
                "thừa; lúc đi tìm lỗi thì nó cứu bạn, vì bạn biết ngay dòng log đó từ đâu ra.</li>"
                "<li><code>as_observation()</code> — gộp trạng thái và nội dung thành một dòng log duy nhất, "
                "nhờ vậy vòng lặp không phải tự ghép chuỗi ở ba chỗ khác nhau.</li>"
                "<li><code>raise NotImplementedError</code> — cố tình để lớp cha nổ. Ai viết tool mới mà quên "
                "cài <code>run()</code> sẽ biết ngay, thay vì nhận về <code>None</code> rồi lỗi ở tận đâu đó "
                "sau này.</li></ul>"
            ),
        },
        {
            "type": "callout",
            "variant": "warn",
            "content": (
                "Hãy để ý sự khác nhau giữa <code>ok()</code> và <code>empty()</code>. <code>empty()</code> "
                "<strong>không phải lỗi</strong>: tool đã chạy đúng, chỉ là không tìm thấy gì. Phân biệt được "
                "hai ca này chính là thứ giúp Agent biết nên thử lại hay nên dừng."
            ),
        },
        {"type": "code", "lang": "bash", "content": "pytest tests/test_tools.py -q"},
        {"type": "callout", "variant": "success", "content": "Output mong đợi: <code>18 passed</code>"},
        {
            "type": "checklist",
            "items": [
                "src/tools/base.py đã tồn tại",
                "pytest tests/test_tools.py -q báo 18 passed",
                "Giải thích được vì sao empty() khác với một exception",
            ],
        },
    ],
}

GOLDEN_PHASE_EXAMPLE = json.dumps(_GOLDEN_PHASE_OBJ, ensure_ascii=False, indent=2)
