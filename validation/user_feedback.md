# 🗣️ Nhật Ký Thử Nghiệm Ngườì Dùng (User Validation Log)

> **Mục tiêu:** Thử nghiệm prototype với $\ge 5$ người dùng thật ngoài nhóm (bao gồm willing users sinh viên môn COMP2010) để đo lường mức độ tin cậy và trải nghiệm thực tế.

---

## 1. Danh Sách Nhật Ký Phản Hồi (Feedback Log)

### 👤 Người thử 1: Nguyễn Văn An (Sinh viên COMP2010 - Willing User #1)
- **Task thực hiện:** Tải Slide Day 05 PDF và tự sinh bài Codelab kết nối LangChain.
- **Quan sát:** Thao tác mượt mà, mất ~3 giây để AI Agent sinh ra Step 2.
- **Trích dẫn nguyên văn:**
  > *"Trước đây xem slide lý thuyết xong em hay bị ngợp không biết bắt đầu viết code từ đâu. Dùng cái này AI nó chia nhỏ thành từng Step có sẵn code mẫu nên em tự tin bấm chạy thử luôn!"*
- **3 Câu hỏi phỏng vấn:**
  1. *Khó chịu nhất:* "Giao diện editor lúc đầu chưa thấy rõ nút Clear terminal."
  2. *Độ tin cậy:* "Rất tin vì code mẫu lấy đúng từ Slide 05 thầy giảng trên lớp."
  3. *Có dùng thật không:* "Có chứ, giúp em làm bài warmup trước giờ lab chiều cực nhanh."
- **Mức độ nghiêm trọng:** Nhẹ (UX minor).

---

### 👤 Người thử 2: Trần Thị Mai (Sinh viên VinUni - Willing User #2)
- **Task thực hiện:** Nhập thử câu hỏi không liên quan "Xin đáp án thi giữa kỳ".
- **Quan sát:** Hệ thống ngay lập tức từ chối và hướng dẫn quay lại làm bài warmup.
- **Trích dẫn nguyên văn:**
  > *"Em thử test xem chatbot có bị lừa cho đáp án không nhưng nó từ chối ngay. Trả lời rất lịch sự và đúng giới hạn."*
- **3 Câu hỏi phỏng vấn:**
  1. *Khó chịu nhất:* "Không có, nút chuyển qua lại giữa VLearn và Codelabs rất rõ."
  2. *Độ tin cậy:* "Tin tưởng 100% vì hệ thống gạt bỏ các câu hỏi ngoài phạm vi."
  3. *Có dùng thật không:* "Chắc chắn dùng để ôn bài."
- **Mức độ nghiêm trọng:** Không có.

---

### 👤 Người thử 3: Lê Hoàng Nam (TA môn COMP2010)
- **Task thực hiện:** Chạy thử code Python trên Terminal và kiểm tra AI Tutor.
- **Quan sát:** Kiểm tra kĩ phần giải thích `temperature=0` của AI Tutor.
- **Trích dẫn nguyên văn:**
  > *"Phần AI Tutor giải thích lý do vì sao dùng temperature=0 rất sát với đáp án môn học. Giúp giảm 70% các câu hỏi lặp lại của sinh viên trên Discord."*
- **3 Câu hỏi phỏng vấn:**
  1. *Khó chịu nhất:* "Nút Tải Slide nên nổi bật hơn nữa ở trang chủ LMS."
  2. *Độ tin cậy:* "Rất cao, trích dẫn đúng trang slide."
  3. *Có dùng thật không:* "Sẽ đề xuất giảng viên đưa vào tài nguyên chính thức của môn."
- **Mức độ nghiêm trọng:** Trung bình (Cần đổi tên/màu nút Slide).

---

### 👤 Người thử 4: Phạm Đức Minh (Học viên khóa AI Product)
- **Task thực hiện:** Thử tải file rỗng và ngắt kết nối mạng.
- **Quan sát:** Thấy thông báo lỗi rõ ràng, không bị crash trang.
- **Trích dẫn nguyên văn:**
  > *"Ấn tượng vì khi em ngắt mạng nó không bị quay mòng mòng mà báo lỗi ngay kèm nút Thử lại."*
- **3 Câu hỏi phỏng vấn:**
  1. *Khó chịu nhất:* "Chưa có chế độ Dark mode cho editor."
  2. *Độ tin cậy:* "Xử lý lỗi chắc chắn."
  3. *Có dùng thật không:* "Có dùng cho các bài lab tiếp theo."
- **Mức độ nghiêm trọng:** Nhẹ.

---

### 👤 Người thử 5: Hoàng Thu Trang (Sinh viên nghỉ buổi học Day 05)
- **Task thực hiện:** Dùng Codelabs để học lại kiến thức buổi nghỉ.
- **Quan sát:** Đã đọc hết Step 1, Step 2 và hoàn thành ở View 3.
- **Trích dẫn nguyên văn:**
  > *"Buổi sáng nghỉ học em sợ không làm được lab chiều, nhờ Codelabs tự sinh từ Slide mà em lấy lại gốc chỉ trong 15 phút."*
- **3 Câu hỏi phỏng vấn:**
  1. *Khó chịu nhất:* "Mong muốn có thêm video minh họa ngắn."
  2. *Độ tin cậy:* "Tin tưởng tuyệt đối."
  3. *Có dùng thật không:* "Rất cần thiết."
- **Mức độ nghiêm trọng:** Nhẹ (Feature request).

---

## 2. Nhật Ký Thay Đổi Từ Phản Hồi (Changelog)

1. **Thay đổi đã thực hiện ngay (Trước Demo):**
   - Đổi tên nút từ *"Slide Bài Giảng Gốc"* thành **`Tải Slide Bài Học (Tự sinh Lab)`** và gắn icon nổi bật (Theo feedback TA Hoàng Nam).
   - Thêm nút **Clear Output** trên Terminal (Theo feedback bạn Văn An).
2. **Quyết định giữ nguyên (Có lý do):**
   - Giữ giao diện Light Theme mặc định của VLearn LMS thay vì Dark Theme toàn trang để đảm bảo tính đồng nhất thương hiệu VinUni.
3. **Đưa vào Backlog (Roadmap tuần tiếp theo):**
   - Tích hợp thêm video hướng dẫn ngắn 30s cho sinh viên nghỉ học.
