# 📝 Báo Cáo Thu Hoạch Cá Nhân (Individual Reflection)

**Họ và tên:** Nguyễn Nhật Minh
**Vai trò trong nhóm:** LLM Integration · Dev · Product Manager
**Dự án:** VLearn Mini Codelab Generator (Nhóm E402)
**Khoá học:** Mini Hackathon AI Batch 03 — VinUni AI Thực Chiến

---

## 1. Phần Việc Đảm Nhận Trong Dự Án
- **Product Manager:** chốt lát cắt MỘT CÂU (`spec.md` §4), bảng impact 3 ứng viên và lý do chọn Ứng viên 2 (`spec.md` §2), phân loại 4 lớp chỗ khó + 8 kịch bản rủi ro (`spec.md` §5).
- **LLM Integration:** thiết kế 2 endpoint gọi OpenAI Chat Completions thật trong `codebase/server.py` —
  `POST /api/generate_minicodelab` (system prompt sinh JSON Mini Codelab 3 bước) và
  `POST /api/run_agent` (mô phỏng log ReAct `[THOUGHT]/[ACTION]/[OBSERVATION]/[FINAL ANSWER]`).
- **Dev:** viết backend `server.py` bằng `http.server` thuần (không framework), xử lý đọc `.env` qua `python-dotenv`, parse/clean JSON output từ LLM, và trả lỗi có hint thay vì crash server khi thiếu API key.
- Viết `description_tutorial.md` — tài liệu chỉ thị ràng buộc cứng (grounding, schema output, non-goals) để giao việc lại cho AI coding agent khi mở rộng tính năng.

## 2. Công Cụ AI Đã Hỗ Trợ Thế Nào?
- **Claude Code:** dùng để đọc lại toàn bộ repo (spec, guide, rubric, codebase) và đối chiếu xem tài liệu mô tả project có khớp với code thật không — phát hiện ra 2 lỗi lệch (mục 3) trước khi để lộ ở demo.
- **OpenAI `gpt-4o-mini`:** là AI call thật ở quyết định trung tâm của sản phẩm (sinh Mini Codelab + chạy sandbox ReAct), không hardcode response — đúng yêu cầu R5 của rubric.

## 3. Bài Học Kinh Nghiệm Từ Case Fail Của Nhóm
- **Trường hợp thất bại thực tế:** Khi rà lại `description_tutorial.md` cùng Claude Code, phát hiện tài liệu mô tả sai bản chất hệ thống ở 2 điểm:
  1. Từng viết "AI đọc trực tiếp slide PDF và repo lab chiều" — nhưng thực tế Coach chỉ chọn 1 trong 3 dòng mô tả cố định trên dropdown, AI không hề parse nội dung file PDF hay code repo thật.
  2. Constraint Policy UI (`app.js`) tick sẵn 2 checkbox `openai` và `pydantic`, nhưng `server.py` không import cả hai — thực tế gọi OpenAI bằng `urllib.request` thuần, dependency thật chỉ có `python-dotenv`.
- **Bài học rút ra:**
  1. *Về sản phẩm:* mô tả "AI làm được gì" (HAX G1/G2) phải khớp chính xác với code, không được nói rộng hơn thực tế — sai chỗ này rất dễ bị TA bắt lỗi ở CP5/CP6 vì chỉ cần hỏi "AI có thật sự đọc file PDF không?" là lộ ngay.
  2. *Về quy trình làm việc với AI agent:* nên để AI đọc chéo-kiểm tra tài liệu spec với code thật định kỳ, thay vì chỉ viết tài liệu một lần rồi tin là đúng — lỗi loại "tài liệu nói một đằng, code làm một nẻo" rất dễ tích luỹ khi nhiều người cùng sửa song song.
