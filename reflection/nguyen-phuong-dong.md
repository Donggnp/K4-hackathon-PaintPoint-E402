# 📝 Báo Cáo Thu Hoạch Cá Nhân (Individual Reflection)

**Họ và tên:** Nguyễn Phương Đông  
**Vai trò trong nhóm:** Lead Developer / AI Integration Engineer  
**Dự án:** VLearn Mini-Codelabs — Slide-to-Lab Platform  
**Khoá học:** VinUni AI Product Hackathon 2026 (Batch 03)  

---

## 1. Phần Việc Đảm Nhận Trong Dự Án
- Xây dựng kiến trúc giao diện Split-screen Codelab Workspace và luồng 3 màn hình (`Overview LMS` ➔ `Codelab Workspace` ➔ `Completion View`).
- Lập trình tính năng **AI Agent Slide-to-Lab Generator**: Đọc và trích xuất mã nguồn mẫu từ Slide bài giảng COMP2010 (`langchain_openai`, `ChatOpenAI`).
- Tích hợp Backend Server Python kết nối OpenAI API để thực thi code và giả lập Terminal Output.
- Xây dựng bộ test **Golden Set (20 cases)** thuộc thư mục `eval/` và đối chiếu với Quality Bar $85\%$.

---

## 2. Công Cụ AI Đã Hỗ Trợ Thế Nào?
- **Cursor / Claude Code:** Hỗ trợ sinh nhanh các UI component với Lucide React icons và Tailwind CSS.
- **ChatGPT / Gemini:** Hỗ trợ thiết kế prompt hệ thống (System Prompt) cho AI Agent để tuân thủ các nguyên tắc HAX (đặc biệt là nguyên tắc **G10 - Thu hẹp phạm vi khi nghi ngờ** và **G11 - Giải thích lý do**).
- **Promptfoo:** Hỗ trợ kiểm thử tự động các trường hợp đầu vào ngẫu nhiên.

---

## 3. Bài Học Kinh Nghiệm Từ Case Fail Của Nhóm
- **Trường hợp thất bại thực tế (TC19):** Khi người dùng nhập code chứa vòng lặp vô hạn `while True: pass`, môi trường giả lập chạy code trên trình duyệt bị trễ phản hồi ngắt timeout (~6 giây thay vì 5 giây cam kết).
- **Bài học rút ra:** 
  1. *Về kỹ thuật:* Việc sandbox và giới hạn tài nguyên tài nguyên phần cứng (Resource Limit) khi thực thi code do AI/người dùng nhập vào cần được xử lý ở tầng Worker độc lập thay vì Main Thread.
  2. *Về sản phẩm:* Thiết kế trải nghiệm theo hướng **Augment** (AI gợi ý, người dùng bấm duyệt và chạy) an toàn và hiệu quả hơn rất nhiều so với việc để AI tự động thực thi tất cả mà không có sự kiểm soát của con người.
