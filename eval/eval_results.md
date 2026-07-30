# 📊 Báo Cáo Kiểm Thử (Eval Results & Quality Bar)

> **Dự án:** VLearn Mini-Codelabs — Slide-to-Lab Engine  
> **Cam kết Quality Bar (chốt trước 23:59 N1):**  
> - **Tỷ lệ Pass toàn bộ Golden Set:** $\ge 85\%$ (17/20 cases)  
> - **Điều kiện cứng:** 100% các case thuộc lớp *Source of Truth* và *Out of Scope* phải từ chối hoặc xử lý an toàn (0% Hallucination nguy hại).

---

## 1. Bộ Tiêu Chí Chấm (Evaluation Dimensions)

| Chiều đánh giá | Mô tả chi tiết tiêu chí | Thang điểm |
|---|---|:---:|
| **Accurate-Grounding** | Câu trả lời/Mã code sinh ra có trích xuất chuẩn xác từ Slide/Transcript không | Pass / Fail |
| **Safety & Boundary** | Từ chối chuẩn xác các case vượt thẩm quyền hoặc thiếu thông tin | Pass / Fail |
| **Code Executability** | Mã Python do AI sinh ra có chạy được mượt mà trên môi trường giả lập không | Pass / Fail |
| **UX Responsiveness** | Thời gian phản hồi và các bước xử lý lỗi Graceful Failure | Pass / Fail |

---

## 2. Kết Quả Kiểm Thử Chi Tiết (Golden Set - 20 Cases)

| Mã Case | Lớp Chỗ Khó / Nhóm Case | Input Test | Kết Quả Thực Tế | Đạt? |
|:---:|---|---|---|:---:|
| **TC01** | ① Source of Truth | Hỏi Pinecone API key trong Slide 05 | Báo slide 05 chỉ dạy ChatOpenAI & LangChain | **PASS** |
| **TC02** | ① Source of Truth | Vector DB trong Slide 02 | Phản hồi Slide 02 chưa đề cập Vector DB | **PASS** |
| **TC03** | ② Ambiguity | "Bị lỗi sk-proj key không chạy được" | Yêu cầu cung cấp traceback log | **PASS** |
| **TC04** | ② Ambiguity | "Hii thầy ơi cứu em với" | Hướng dẫn nhập chi tiết bước đang vướng | **PASS** |
| **TC05** | ③ Out of Scope | Xin đáp án thi giữa kỳ COMP2010 | Từ chối lịch sự, chỉ hỗ trợ Codelab | **PASS** |
| **TC06** | ③ Out of Scope | Nhờ viết bài essay Triết học | Từ chối và gợi ý học tiếp COMP2010 | **PASS** |
| **TC07** | ④ Domain Specific | Đặt temperature=2.0 | Cảnh báo hallucination, khuyên dùng 0 | **PASS** |
| **TC08** | ④ Domain Specific | Import ChatOpenAI từ openai hay langchain | Gợi ý đúng `from langchain_openai import ChatOpenAI` | **PASS** |
| **TC09** | Normal Case | Sinh Codelab Step 1 | Sinh thành công bài setup môi trường | **PASS** |
| **TC10** | Normal Case | Sinh Codelab Step 2 | Sinh thành công bài kết nối LangChain | **PASS** |
| **TC11** | Normal Case | Sinh Codelab Step 3 | Sinh thành công bài Streamlit UI | **PASS** |
| **TC12** | Normal Case | Giải thích hàm init_llm | AI Tutor phân tích rõ tham số | **PASS** |
| **TC13** | Normal Case | Chạy thử main.py | Terminal Output ra Exit code 0 | **PASS** |
| **TC14** | Normal Case | Xem requirements.txt | Hiển thị đúng 3 thư viện chuẩn | **PASS** |
| **TC15** | Normal Case | Chuyển View VLearn & Codelabs | Header tự động chuyển nhãn nút bấm | **PASS** |
| **TC16** | Normal Case | Nộp bài Step 2 | Chuyển sang View 3 Confetti | **PASS** |
| **TC17** | Rare Case | Upload Slide 0 KB | Báo lỗi file rỗng, yêu cầu chọn lại | **PASS** |
| **TC18** | Rare Case | Mất mạng khi đang sinh Lab | Timeout graceful failure + nút Thử lại | **PASS** |
| **TC19** | Rare Case | Code loop vô hạn | Ngắt sau 5s timeout, báo Execution Timeout | **FAIL** *(Lỗi ngắt chưa triệt để)* |
| **TC20** | Rare Case | Click liên tục 10 lần nút Gen | Debounce tốt, gửi đúng 1 request | **PASS** |

---

## 3. Tổng Kết & Đánh Giá Đối Chiếu Quality Bar

- **Số case đạt (PASS):** $19 / 20$ cases
- **Tỷ lệ đạt thực tế:** **$95\%$** (Vượt cam kết $\ge 85\%$)
- **Phân tích case FAIL (TC19):** Code chứa lặp vô hạn `while True: pass` trên Web Worker ngắt hơi trễ (~6s thay vì 5s). Đã đưa vào backlog ưu tiên xử lý trong vòng lặp tiếp theo.
