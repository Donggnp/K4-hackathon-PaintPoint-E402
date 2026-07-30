# 📝 Báo Cáo Thu Hoạch Cá Nhân (Individual Reflection)

**Họ và tên:** Nguyễn Quý Dũng
**Vai trò trong nhóm:** Leader
**Dự án:** VLearn Mini-Codelabs — Slide-to-Lab Platform  
**Khoá học:** VinUni AI Product Hackathon 2026 (Batch 03)  

---

## 1. Phần Việc Đảm Nhận Trong Dự Án

- **Định hướng chiến lược & Quản trị dự án (Product Leadership):** Xác định đúng bài toán cốt lõi (Pain point học viên lạm dụng AI gõ prompt mà không hiểu bản chất lý thuyết đã học), định hình lát cắt sản phẩm **VLearn Mini-Codelabs Bridge (Sáng ➔ Chiều)** và bảo vệ quyết định lựa chọn giải pháp trong `spec.md`.
- **Điều phối công việc & Phân công nguồn lực:** Phân công nhiệm vụ rõ ràng và gắn kết giữa các mảng Backend/LLM (Minh), Frontend/Sandbox (Đông) và UX/Validation (Trang); điều phối các mốc tiến độ đảm bảo hoàn thành đúng thời hạn Hackathon.
- **Xây dựng & Phân tích bằng chứng khảo sát (Survey Analysis & Evidence):** Trực tiếp xử lý và tổng hợp dữ liệu khảo sát định lượng từ 28 học viên (file `validation/Khảo sát về việc học lý thuyết và thực hành lab.csv`), trích xuất các chỉ số thuyết phục ($96.4\%$ nhu cầu Mini Codelab, $89.3\%$ gặp khó nếu không có AI) để củng cố phần Evidence trong `spec.md`.
- **Rà soát tiêu chuẩn chất lượng (Quality Bar & Rubric Alignment):** Đóng vai trò kiểm soát chất lượng, đối chiếu sản phẩm với các tiêu chí Rubric Hackathon (R1-R6), đảm bảo tích hợp chuẩn 4 nguyên tắc HAX/PAIR (`G1`, `G2`, `G9`, `G10`) và chuẩn bị kịch bản thuyết trình Demo.

---

## 2. Công Cụ AI Đã Hỗ Trợ Thế Nào?

- **ChatGPT / Claude Code:** Hỗ trợ phân rã công việc (WBS), tổng hợp và phân tích dữ liệu định lượng từ file khảo sát CSV, cũng như rà soát các điểm mâu thuẫn giữa Spec và Codebase.
- **Gemini / Antigravity Agent:** Hỗ trợ tự động hóa việc cập nhật tài liệu dự án (`spec.md`), trích xuất số liệu thống kê chuẩn xác và kiểm tra tính nhất quán trong báo cáo dự án.
- **Promptfoo & Golden Set Analysis:** Phối hợp cùng Lead Dev rà soát và đánh giá bộ test Golden Set (20 cases) thuộc thư mục `eval/` để đảm bảo hệ thống đạt Quality Bar $85\%$.

---

## 3. Bài Học Kinh Nghiệm Từ Case Fail Của Nhóm

- **Trường hợp thất bại thực tế (Sự lệch pha giữa Spec & Codebase và nhãn UX HAX G1):** 
  Trong quá trình rà soát dự án, nhóm từng gặp 2 vấn đề:
  1. Tài liệu mô tả chưa khớp với thực thi code (ghi AI đọc trực tiếp file PDF thay vì gọi prompt sinh theo chủ đề slide).
  2. Tên nút bấm ban đầu (*"Slide Bài Giảng Gốc"*) khiến người dùng nhầm là file PDF tĩnh thay vì nút kích hoạt AI Agent.
- **Bài học rút ra:**
  1. *Về quản trị dự án (HAX G1/G2):* Leader phải giữ vai trò cầu nối kiểm tra chéo liên tục giữa Spec và Codebase thực tế. "Nói đúng - Làm chuẩn" những gì AI thực hiện là chìa khóa để giữ độ tin cậy của sản phẩm trước người dùng và Hội đồng giám khảo.
  2. *Về triết lý sản phẩm AI (Augment vs Automate):* Thiết kế sản phẩm AI trong giáo dục phải theo hướng **Augment** (AI hỗ trợ chia nhỏ bài tập và giải thích - Học viên tự bấm duyệt và chạy code) để đảm bảo học viên thực sự tích tụ kiến thức thay vì phó mặc hoàn toàn cho AI.
