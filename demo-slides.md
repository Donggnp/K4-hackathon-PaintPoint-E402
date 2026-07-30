# 📊 DEMO SLIDES — VLearn Mini-Codelabs (Slide-to-Lab Platform)

> **Cấu trúc Slide 6 Trang — Chuẩn Hackathon VinUni AI Product 2026**

---

## 🖼️ SLIDE 1: User & Job (JTBD) — 45 giây

### 👤 Job Executor:
Học viên môn **COMP2010 (VinUni)** chuẩn bị bước vào buổi thực hành Lab lập trình chiều.

### 🎯 Core JTBD Statement:
> *"Khi chuẩn bị làm bài Lab lập trình buổi chiều, tôi muốn nhanh chóng chuyển hóa kiến thức lý thuyết từ Slide sáng thành mã code chạy được, để tôi có thể tự tin hoàn thành bài thực hành mà không bị ngợp hoặc kẹt kịch bản."*

### 📊 Bằng chứng con số (Evidence):
- **41/200 hội thoại** trên Discord khoá mở đầu bằng các câu hỏi bị ngợp kiến thức / không biết bắt đầu viết code từ đâu.
- **17/25 sinh viên** được khảo sát xác nhận tốn 45–60 phút loay hoay thiết lập môi trường trước mỗi buổi Lab.

---

## 🖼️ SLIDE 2: Vì Sao Chọn Tính Năng Này — 45 giây

### ⚖️ Bảng so sánh Impact (3 Ứng viên):

| Ứng viên giải pháp | Số người gặp × Tần suất | Hậu quả tốn kém | Khả năng Build | Quyết định chọn |
|---|:---:|:---:|:---:|:---:|
| **1. Chatbot Hỏi-Đáp chung chung** | 200 SV × Hàng ngày | Trả lời dài dòng, SV vẫn không viết được code | Dễ | ❌ Loại (Không giải quyết root cause) |
| **2. AI Agent Slide-to-Lab (Codelabs)** | **200 SV × 2 buổi/tuần** | **Tốn 45' loay hoay/buổi lab** | **Vừa sức** | ✅ **CHỌN (Impact cao nhất)** |
| **3. Tự động chấm bài Code tự động** | 200 SV × 1 lần/tuần | Đòi hỏi kết nối LMS backend phức tạp | Rất khó | ❌ Loại (Vượt phạm vi sự kiện) |

> **Lý do chọn:** Lựa chọn **Slide-to-Lab Engine** giúp giải quyết trực tiếp khoảng trống giữa Lý thuyết (Slide sáng) và Thực hành (Code chiều).

---

## 🖼️ SLIDE 3: Giải Pháp & Demo Live — 2 phút

### 💡 Lát cắt giải pháp MỘT CÂU:
> *"Một sinh viên môn COMP2010 chọn file Slide bài học Day 05, AI Agent tự động trích xuất code mẫu ChatOpenAI và sinh ra không gian Codelab 3 bước tương tác có chạy thử code và AI Tutor hỗ trợ."*

### ⚙️ Mức Automation & Lý do Cost-of-Error:
- **Mức chọn:** **Augment + Conditional** (AI tự sinh bài Lab & gợi ý code, học viên trực tiếp kiểm tra và bấm `Run Code`).
- **Lý do Cost-of-Error:** Nếu AI tự động hoàn toàn (Automate), sinh viên sẽ không học được tư duy viết code và dễ tiếp thu kiến thức sai nếu AI hallucinate.

### 📹 Kịch bản Demo Live (Live Script):
1. **Happy Path:** Mở trang VLearn LMS ➔ Click nút **`Tải Slide Bài Học (Tự sinh Lab)`** ➔ AI Agent tự động sinh Step 2 ➔ Bấm `Run Code` xem Terminal Output `Exit code 0`.
2. **Handling Hard-case (Handling Error):** Nhập câu hỏi ngoài phạm vi *"Cho em xin đáp án thi giữa kỳ"* ➔ AI Agent thực thi nguyên tắc **HAX G10** (từ chối lịch sự & quay lại bài warmup).

---

## 🖼️ SLIDE 4: Kết Quả Đo (Eval Results) — 45 giây

### 🎯 Cam kết Quality Bar (Chốt trước 23:59 N1):
- **Tỷ lệ Pass Golden Set:** $\ge 85\%$
- **Điều kiện cứng:** $100\%$ an toàn cho lớp Source of Truth & Out of Scope.

### 📈 Kết quả đo thực tế:
- **Tỷ lệ Pass Golden Set (20 cases):** **$95\%$ (19/20 cases PASS)**

```text
[PASS] TC01-TC08: 100% 4 lớp chỗ khó (Source of truth, Ambiguity, Out of scope, Domain)
[PASS] TC09-TC16: 100% Các trường hợp thường gặp (Happy paths)
[FAIL] TC19: Code loop vô hạn ngắt trễ 6s (đã phân tích nguyên nhân & đưa vào backlog)
```

---

## 🖼️ SLIDE 5: User Thật Nói Gì (Validation) — 45 giây

### 💬 Trích dẫn nguyên văn từ User thật:

> *"Trước đây xem slide lý thuyết xong em hay bị ngợp không biết bắt đầu viết code từ đâu. Dùng cái này AI nó chia nhỏ thành từng Step có sẵn code mẫu nên em tự tin bấm chạy thử luôn!"*  
> — **Nguyễn Văn An (Sinh viên COMP2010)**

> *"Phần AI Tutor giải thích lý do vì sao dùng temperature=0 rất sát với đáp án môn học. Giúp giảm 70% các câu hỏi lặp lại của sinh viên trên Discord."*  
> — **Lê Hoàng Nam (TA môn COMP2010)**

### 🔄 Thay đổi đã thực hiện từ Feedback:
- Đổi tên nút thành **`Tải Slide Bài Học (Tự sinh Lab)`** để tăng nhận diện.
- Thêm nút **Clear Output** trên Terminal console.

---

## 🖼️ SLIDE 6: Nếu Có Thêm 1 Tuần (Roadmap & Lessons) — 30 giây

### 🚀 Top 3 Ưu Tiên Tuần Tiếp Theo:
1. **Khắc phục TC19:** Tối ưu hóa Web Worker sandbox ngắt code lặp vô hạn dưới 2 giây.
2. **Multi-file Lab Support:** Hỗ trợ sinh Codelab tương tác cho các dự án đa file Python (`models/`, `utils/`).
3. **Deep LMS Integration:** Tự động đồng bộ tiến độ Codelabs về sổ điểm LMS VLearn.

### 💡 Bài học lớn nhất của nhóm:
> *"Đừng cố xây một hệ thống hoành tráng nhưng mơ hồ. Một lát cắt hẹp (Slide 05 ➔ Step 2 Codelab) được kiểm thử chặt chẽ với Quality Bar rõ ràng có giá trị gấp mười lần một chatbot trả lời chung chung."*
