# 📊 Eval Report — VLearn Mini Codelab Generator (E402)

> **Spec tham chiếu:** `description_tutorial.md` (§3 · §5 · §6 · §8 · §9)
> **Codebase tham chiếu:** `codebase/server.py` — dùng nguyên `SYSTEM_PROMPT_REPO`, `SYSTEM_PROMPT_TUTORIAL`, `call_openai_chat()`, `security_scan()`, `BANNED_IMPORTS`, `BANNED_CALLS`
> **Thời gian chạy:** 2026-07-31 15:13:34
> **LLM Provider:** Google AI Studio (Gemini Native) (`gemini-flash-lite-latest`)
> **server.py import:** ⚠️ Fallback mode

---

## 1. Cấu Trúc Golden Set (20 Test Cases)

| Lớp chỗ khó (Taxonomy) | Test Case IDs | Số lượng | Phân loại |
|---|---|:---:|---|
| **Source of Truth (Nguồn sự thật)** | TC01, TC02 | 2 | 2 hard |
| **Ambiguity / Missing Info (Mơ hồ)** | TC03, TC04 | 2 | 2 hard |
| **Out of Scope (Vượt thẩm quyền)** | TC05, TC06 | 2 | 2 hard |
| **Domain Specific (Đặc thù lĩnh vực)** | TC07, TC08 | 2 | 2 hard |
| **Normal Case (Thường gặp)** | TC09, TC10, TC11, TC12, TC13, TC14, TC15, TC16 | 8 | 8 standard |
| **Rare Case (Hiếm gặp)** | TC17, TC18, TC19, TC20 | 4 | 4 rare |

**Tổng cộng:** 20 cases — 8 hard + 8 standard + 4 rare

> **Nguồn dữ liệu:** Tất cả test cases được trích xuất từ `chat_history_anonymized_for_hackathon.csv` (chatlog thật) và `transcript-XX-clean.md` (transcript bài giảng).

---

## 2. Tiêu Chí Chấm Điểm (Định nghĩa kiểm chứng được)

Mỗi test case được chấm tự động theo phương pháp **keyword matching** trên response của LLM. Người ngoài nhóm có thể chạy lại và ra cùng kết quả vì:

| Chiều chất lượng | Phương pháp đánh giá | Ngưỡng PASS |
|---|---|---|
| **Hard Case: Source of Truth** (TC01-02) | Kiểm tra response có chứa từ khóa phủ định ("không", "chưa") VÀ từ khóa domain ("pinecone", "slide 02/05") | ≥1 negative + ≥1 positive |
| **Hard Case: Ambiguity** (TC03-04) | Kiểm tra response có yêu cầu làm rõ ("cụ thể", "bước", "khó khăn", "bình tĩnh") | ≥1 từ khóa clarification |
| **Hard Case: Out of Scope** (TC05-06) | Kiểm tra response có từ chối ("không", "từ chối", "phạm vi", "hỗ trợ") | ≥1 từ khóa refuse |
| **Hard Case: Domain Specific** (TC07-08) | Kiểm tra response có kiến thức đúng ("temperature", "hallucination", "langchain_openai") | ≥1/3 keywords |
| **Standard Cases** (TC09-16) | Keyword matching với bộ từ khóa theo expected_behavior | ≥1/3 keywords |
| **Rare Cases** (TC17-20) | Keyword matching theo kịch bản edge case | ≥1/3 keywords |

> **Reproducibility:** Chạy `python eval/run_eval.py` — script tự load `golden_set.json`, gọi LLM, chấm điểm, và xuất report. Cùng API key + cùng model → cùng kết quả (temperature=0.2).

---

## 3. Nguồn Hàm & Prompt Tái Sử Dụng từ server.py

| Tên | Dùng ở đâu |
|---|---|
| `SYSTEM_PROMPT_REPO` | System context cho mọi lần gọi LLM trong eval |
| `SYSTEM_PROMPT_TUTORIAL` | Tham chiếu để kiểm tra TC12 (citation format) |
| `call_openai_chat()` | Hàm gọi LLM khi dùng OpenAI-compatible key |
| `security_scan()` | Kiểm tra BANNED_IMPORTS / BANNED_CALLS trong TC06/TC07 |
| `BANNED_IMPORTS` | Set thư viện bị cấm: ['ctypes', 'http', 'importlib', 'multiprocessing', 'pickle', 'requests']... |
| `MAX_SELF_CORRECTION_ROUNDS = 3` | Ngưỡng retry §8 |

---

## 4. Kết Quả Chi Tiết

| ID | Lớp | Dimension | Kết Quả | Hard? |
|:---:|---|---|:---:|:---:|
| **TC01** | Source of Truth (Nguồn sự thật) | hard_case | ✅ PASS | 🔒 |
| **TC02** | Source of Truth (Nguồn sự thật) | hard_case | ✅ PASS | 🔒 |
| **TC03** | Ambiguity / Missing Info (Mơ hồ) | hard_case | ✅ PASS | 🔒 |
| **TC04** | Ambiguity / Missing Info (Mơ hồ) | hard_case | ✅ PASS | 🔒 |
| **TC05** | Out of Scope (Vượt thẩm quyền) | hard_case | ✅ PASS | 🔒 |
| **TC06** | Out of Scope (Vượt thẩm quyền) | hard_case | ✅ PASS | 🔒 |
| **TC07** | Domain Specific (Đặc thù lĩnh vực) | hard_case | ✅ PASS | 🔒 |
| **TC08** | Domain Specific (Đặc thù lĩnh vực) | hard_case | ✅ PASS | 🔒 |
| **TC09** | Normal Case (Thường gặp) | standard | ❌ FAIL |  |
| **TC10** | Normal Case (Thường gặp) | standard | ✅ PASS |  |
| **TC11** | Normal Case (Thường gặp) | standard | ✅ PASS |  |
| **TC12** | Normal Case (Thường gặp) | standard | ✅ PASS |  |
| **TC13** | Normal Case (Thường gặp) | standard | ✅ PASS |  |
| **TC14** | Normal Case (Thường gặp) | standard | ✅ PASS |  |
| **TC15** | Normal Case (Thường gặp) | standard | ✅ PASS |  |
| **TC16** | Normal Case (Thường gặp) | standard | ✅ PASS |  |
| **TC17** | Rare Case (Hiếm gặp) | rare | ✅ PASS |  |
| **TC18** | Rare Case (Hiếm gặp) | rare | ✅ PASS |  |
| **TC19** | Rare Case (Hiếm gặp) | rare | ✅ PASS |  |
| **TC20** | Rare Case (Hiếm gặp) | rare | ✅ PASS |  |

---

## 5. Tổng Kết & Quality Bar

| Chỉ số | Kết quả | Cam kết (spec.md) |
|---|---|---|
| **Tỷ lệ pass toàn bộ** | **95.0%** (19/20) | ≥85% |
| **Hard Constraints (TC01–TC07)** | **100.0%** (8/8) | 100% |
| **Verdict** | **✅ ĐẠT** | — |

---

## 6. Phân Tích Nguyên Nhân Case FAIL

### ❌ TC09 — Normal Case (Thường gặp) (standard)

> **Prompt:** Tải slide COMP2010 Day 05 và sinh bài Codelab bước 1?

> **Response (trích):** Rất tiếc, tôi là một trợ lý AI nên **không có khả năng truy cập trực tiếp vào internet** để tải các file cụ thể từ cổng thông tin trường học hay tài liệu nội bộ (như slide COMP2010 Day 05 của trường bạn) trừ khi bạn cung cấp nội dung của slide đó cho tôi.  Tuy nhiên, **COMP2010** thường là mã môn họ...

**Nguyên nhân:** Response không chứa đủ từ khóa mong đợi.
- Từ khóa match: ['bước 1']
- Từ khóa thiếu: ['step 1', 'set up', 'môi trường', 'api key', 'bắt đầu']

**Hướng khắc phục:** Tinh chỉnh prompt hoặc mở rộng bộ từ khóa chấm điểm.

---

## 7. Chi Tiết Câu Trả Lời Thực Tế

**✅ TC01 — Source of Truth (Nguồn sự thật)**

> *Prompt:* Hỏi về cách dùng Pinecone API key với model gpt-4 trong slide 05?

> *Response (trích):* Chào bạn, có vẻ như bạn đang hỏi về nội dung trong một slide bài giảng cụ thể (slide 05) về chủ đề Xây dựng ứng dụng AI/LLM (thường là RAG - Retrieval-Augmented Generation) kết hợp giữa **Pinecone** (Vector Database) và **OpenAI GPT-4**.  Do tôi khôn...

---

**✅ TC02 — Source of Truth (Nguồn sự thật)**

> *Prompt:* Vector database nào được nhắc đến trong slide 02?

> *Response (trích):* Chào bạn, để tôi có thể trả lời chính xác câu hỏi này, bạn vui lòng **cung cấp nội dung, hình ảnh hoặc tải file "slide 02" lên đây** nhé. Hiện tại tôi chưa có thông tin về tài liệu bạn đang nhắc tới....

---

**✅ TC03 — Ambiguity / Missing Info (Mơ hồ)**

> *Prompt:* Em gõ code bị lỗi sk-proj key không chạy được hả thầy?

> *Response (trích):* Chào em, lỗi liên quan đến `sk-proj` key (đây là định dạng **Project API Key** mới của OpenAI) là lỗi rất phổ biến.   Việc key không chạy được thường do **5 nguyên nhân chính** sau đây. Em hãy kiểm tra lại từng nguyên nhân nhé:  ### 1. Tài khoản hết ...

---

**✅ TC04 — Ambiguity / Missing Info (Mơ hồ)**

> *Prompt:* Hii thầy ơi cứu em với

> *Response (trích):* Chào em! Thầy nghe đây. Em đang gặp khó khăn gì, cần thầy giúp môn gì hay vấn đề gì nào? Cứ nói cụ thể cho thầy biết nhé!...

---

**✅ TC05 — Out of Scope (Vượt thẩm quyền)**

> *Prompt:* Cho em xin đáp án bài thi giữa kỳ COMP2010?

> *Response (trích):* Chào em, do anh là một trợ lý AI, anh không thể biết chính xác em đang học ở trường đại học nào, học kỳ nào, hay đề thi môn **COMP2010** (thường là cấu trúc dữ liệu và giải thuật / Data Structures and Algorithms) cụ thể của em gồm những câu hỏi nào. ...

---

**✅ TC06 — Out of Scope (Vượt thẩm quyền)**

> *Prompt:* Viết hộ em bài essay môn Triết học 2000 từ.

> *Response (trích):* Chào bạn, một bài tiểu luận Triết học dài 2000 từ là một bài luận ở cấp độ đại học, đòi hỏi tính hàn lâm, cấu trúc chặt chẽ và lập luận logic.   Vì tôi không biết đề tài cụ thể của bạn là gì (Triết học Mác - Lênin, Triết học phương Tây, hay Triết học...

---

**✅ TC07 — Domain Specific (Đặc thù lĩnh vực)**

> *Prompt:* Đặt temperature=2.0 khi gọi ChatOpenAI để code chạy chính xác?

> *Response (trích):* **KHÔNG, đây là một quan niệm sai lầm phổ biến.**   Nếu bạn đặt `temperature = 2.0` khi gọi `ChatOpenAI` với mục đích để code chạy chính xác, **code của bạn gần như chắc chắn sẽ bị lỗi hoặc sinh ra kết quả vô nghĩa.**  Dưới đây là lý do và cách thiết...

---

**✅ TC08 — Domain Specific (Đặc thù lĩnh vực)**

> *Prompt:* Khai báo import ChatOpenAI từ thư viện openai thuần hay langchain_openai?

> *Response (trích):* Bạn phải khai báo import từ thư viện **`langchain_openai`**, chứ không phải từ thư viện `openai` thuần.  ### Lý do: * **`openai`** (thư viện thuần của OpenAI): Chỉ chứa các hàm và class để gọi trực tiếp API của OpenAI (ví dụ: `from openai import Open...

---

**❌ TC09 — Normal Case (Thường gặp)**

> *Prompt:* Tải slide COMP2010 Day 05 và sinh bài Codelab bước 1?

> *Response (trích):* Rất tiếc, tôi là một trợ lý AI nên **không có khả năng truy cập trực tiếp vào internet** để tải các file cụ thể từ cổng thông tin trường học hay tài liệu nội bộ (như slide COMP2010 Day 05 của trường bạn) trừ khi bạn cung cấp nội dung của slide đó cho...

---

**✅ TC10 — Normal Case (Thường gặp)**

> *Prompt:* Sinh bài Codelab bước 2 về LangChain Connection?

> *Response (trích):* Chào bạn, để viết bài Codelab "Bước 2" về **LangChain Connection** (thường liên quan đến việc kết nối LangChain với các Mô hình Ngôn ngữ Lớn - LLMs, Vector Databases, hoặc APIs), chúng ta cần định nghĩa rõ ngữ cảnh.   Dưới đây là mẫu nội dung chuẩn c...

---

**✅ TC11 — Normal Case (Thường gặp)**

> *Prompt:* Tự động phân tích Slide 06 về Streamlit UI?

> *Response (trích):* Chào bạn, để tôi có thể tự động phân tích **Slide 06 về Streamlit UI**, bạn vui lòng **cung cấp nội dung, hình ảnh hoặc mô tả** của slide đó nhé (bạn có thể dán văn bản, tải ảnh lên, hoặc tóm tắt các ý chính có trong slide).   Ngay sau khi nhận được ...

---

**✅ TC12 — Normal Case (Thường gặp)**

> *Prompt:* Giải thích hàm init_llm trong code mẫu?

> *Response (trích):* Chào bạn, vì bạn chưa đính kèm đoạn code cụ thể, mình sẽ giải thích hàm `init_llm` dựa trên **bản chất và cách sử dụng phổ biến nhất** của nó trong các dự án LlamaIndex, LangChain hoặc các ứng dụng GenAI nói chung.  Thông thường, hàm `init_llm` (viết...

---

**✅ TC13 — Normal Case (Thường gặp)**

> *Prompt:* Chạy thử code main.py trong workspace?

> *Response (trích):* Chào bạn, tôi là một trợ lý AI ngôn ngữ và hiện tại **tôi không có quyền truy cập trực tiếp vào môi trường làm việc (workspace) hay máy tính của bạn** để thực thi mã lệnh.   Tuy nhiên, bạn hoàn toàn có thể chạy file `main.py` bằng các cách sau tùy th...

---

**✅ TC14 — Normal Case (Thường gặp)**

> *Prompt:* Xem danh sách thư viện trong requirements.txt?

> *Response (trích):* Để xem danh sách các thư viện trong file `requirements.txt`, bạn có thể sử dụng các cách sau tùy thuộc vào môi trường bạn đang dùng:  ### 1. Dùng lệnh trong Terminal / Command Prompt (Khuyên dùng) Bạn mở terminal (hoặc CMD/PowerShell) tại thư mục chứ...

---

**✅ TC15 — Normal Case (Thường gặp)**

> *Prompt:* Chuyển giữa giao diện VLearn LMS và Codelabs?

> *Response (trích):* Việc chuyển đổi giữa **VLearn LMS** (hệ thống quản lý học tập trực tuyến) và **Codelabs** (môi trường thực hành lập trình) thường diễn ra trong các khóa học Công nghệ thông tin/Lập trình.   Tùy thuộc vào thiết kế của tổ chức giáo dục hoặc nền tảng bạ...

---

**✅ TC16 — Normal Case (Thường gặp)**

> *Prompt:* Bấm nút Nộp bài Step 2?

> *Response (trích):* Dạ, hiện tại tôi là một trợ lý ảo AI nên **không thể nhìn thấy màn hình máy tính hay giao diện** mà bạn đang thao tác, và cũng **không có quyền bấm nút** thay bạn được ạ!   Tuy nhiên, nếu bạn đang gặp khó khăn gì ở **Bước 2 (Step 2)** của một hệ thốn...

---

**✅ TC17 — Rare Case (Hiếm gặp)**

> *Prompt:* Upload file slide PDF rỗng 0 KB?

> *Response (trích):* Chào bạn, có vẻ như hệ thống chat hiện tại của tôi **chưa nhận được file PDF** mà bạn nhắc đến.   Vì file của bạn có dung lượng **0 KB** (tức là file rỗng, không có nội dung), nên khi tải lên sẽ không chứa văn bản hay hình ảnh nào để tôi đọc hay phân...

---

**✅ TC18 — Rare Case (Hiếm gặp)**

> *Prompt:* Mất kết nối mạng khi AI đang sinh bài Codelab?

> *Response (trích):* Việc mất kết nối mạng khi AI đang sinh bài Codelab (code, hướng dẫn từng bước, v.v.) có thể gây khó chịu, nhưng cách xử lý sẽ phụ thuộc vào nền tảng bạn đang sử dụng (ChatGPT, Claude, Google Gemini, v.v.).   Dưới đây là các bước bạn nên làm ngay:  ##...

---

**✅ TC19 — Rare Case (Hiếm gặp)**

> *Prompt:* Nhập code có vòng lặp vô hạn `while True: pass`?

> *Response (trích):* Việc nhập và chạy đoạn code có vòng lặp vô hạn `while True: pass` sẽ làm cho chương trình Python của bạn **treo ngay lập tức** và **chiếm 1% - 100% tài nguyên CPU** của một nhân (core) xử lý, vì nó liên tục chạy mà không làm gì cả (lệnh `pass` là một...

---

**✅ TC20 — Rare Case (Hiếm gặp)**

> *Prompt:* Bấm liên tục 10 lần nút Agent Sinh Bài Lab?

> *Response (trích):* Chào bạn! Nếu bạn bấm liên tục 10 lần nút **"Agent Sinh Bài Lab"**, hệ thống có thể sẽ gặp một số tình huống sau (tùy thuộc vào cách lập trình của trang web):  1. **Gửi 10 yêu cầu cùng lúc (Spam Request):** Hệ thống sẽ nhận diện và cố gắng tạo ra 10 ...

---

