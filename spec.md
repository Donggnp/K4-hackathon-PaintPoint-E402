# AI SPEC — Mini Codelab Generator cho VLearn · Nhóm E402 · Zone Hackathon
Hướng: [x] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [ ] Tối ưu tính năng có sẵn  [x] Tính năng mới

## §1. User & Job
- **Job executor + workflow**: Học viên khoá AI Thực Chiến (đang trong buổi học sáng lý thuyết và chuẩn bị làm bài codelab 4 tiếng buổi chiều).
- **Core JTBD**: Học và hiểu sâu bản chất lý thuyết AI (AI Agent, Product Design) để làm bài thực hành codelab buổi chiều trơn tru và tự tin, không bị phụ thuộc lạm dụng AI code generation khiến mất niềm tin và khó hiểu bài.
- **Problem statement**: Học viên tham gia bài thực hành codelab 4 tiếng buổi chiều dưới áp lực thời gian gấp gáp, thường lạm dụng AI gõ prompt copy-paste code mà không hiểu rõ bản chất lý thuyết đã học buổi sáng, dẫn đến gặp lỗi không biết cách sửa và khó tích hội tụ kiến thức.
- **Evidence**:
  - Số liệu mining / kết quả khảo sát: 
    - Khảo sát 20/20 học viên lớp AI Thực Chiến (85% gặp áp lực bài lab 4 tiếng và muốn có bài Mini Lab 15 phút buổi sáng).
    - Phân tích chi tiết từ file khảo sát 28 học viên ([Khảo sát về việc học lý thuyết và thực hành lab.csv](file:///d:/HocTap/AIinAction/K4-hackathon-PaintPoint-E402/validation/Kh%E1%BA%A3o%20s%C3%A1t%20v%E1%BB%81%20vi%E1%BB%87c%20h%E1%BB%8Dc%20l%C3%BD%20thuy%E1%BA%BFt%20v%C3%A0%20th%E1%BB%B1c%20h%E1%BB%8Dc%20lab.csv)):
      + **96.4%** (27/28) học viên sẵn sàng làm bài Mini Codelab ngắn (15–30 phút) ngay sau giờ lý thuyết để hiểu sâu workflow và tự code from scratch (57.1% chắc chắn làm, 39.3% làm khi rảnh).
      + **89.3%** (25/28) học viên gặp khó khăn lớn hoặc không tự làm được bài lab nếu không dùng AI (67.9% chỉ làm được một ít, 21.4% không làm được tí nào).
      + **64.3%** (18/28) học viên nhận thấy khoảng cách lớn giữa lý thuyết buổi sáng và thực hành lab chiều ("hiểu lý thuyết nhưng bài lab khó nếu không dùng AI").
      + **53.6%** (15/28) học viên sau buổi lab vẫn chỉ "hơi hơi" hoặc "không hiểu tí gì" về workflow & code implementation thực tế.
      + **67.9%** (19/28) học viên cho biết chỉ tiếp thu được $\le 50\%$ kiến thức khi chỉ nghe giảng lý thuyết slide buổi sáng.
  - ≥5 quote/ví dụ nguyên văn + nguồn:
    1. *"Buổi sáng nghe slide ReAct hay lắm nhưng đến chiều đụng bài lab 4 tiếng ngợp quá, chỉ biết nhờ ChatGPT viết giùm mà không hiểu nó chạy sao."* (Học viên U04)
    2. *"Giá như sáng có bài test code nhỏ 15 phút làm lại theo slide thì chiều đỡ mất 1 tiếng rưỡi chỉ để setup environment và mò prompt."* (Học viên U12)
    3. *"Dùng AI gen code chiều rất gấp, lỗi một cái là đứng hình vì không nắm chắc luồng Thought-Action của Agent."* (Học viên U08)
    4. *"Giảng viên giảng slide lý thuyết rất chuẩn nhưng khoảng cách từ slide đến bài code lab 4 tiếng quá xa."* (Học viên U15)
    5. *"Lab Coach muốn tạo bài tập nhỏ buổi sáng hỗ trợ học viên nhưng không có đủ thời gian soạn repo mini riêng cho từng buổi."* (Lab Coach M02)

## §2. Impact & quyết định chọn
- **Bảng impact ≥3 ứng viên**:
  | Ứng viên | Bao nhiêu người | Tần suất | Tốn gì mỗi lần | Khả thi | Chọn? |
  |---|---|---|---|---|---|
  | 1. AI Tutor giải đáp thắc mắc realtime trên VLearn | ~1.000 học viên | Hàng ngày | 15-20 phút hỏi qua lại | Khả thi nhưng đã có sẵn | Không |
  | 2. AI Generator sinh Mini Codelab cầu nối (Sáng ➔ Chiều) | ~1.000 học viên | Mỗi ngày học | 1.5 - 2 tiếng mệt mỏi ở lab chiều | Rất khả thi (1.5 ngày) | **CHỌN** |
  | 3. AI Tự động chấm điểm và viết unit test cho bài lab chiều | ~1.000 học viên | Cuối buổi chiều | 30 phút tự test | Phức tạp, vượt phạm vi | Không |

- **Ứng viên ĐÃ LOẠI + vì sao**: Loại Ứng viên 1 (đã có tính năng tutor baseline) và Ứng viên 3 (đòi hỏi hạ tầng sandbox phức tạp, cost-of-error cao).
- **Ứng viên CHỌN + vì sao (bằng số)**: Chọn Ứng viên 2 vì giải quyết trực tiếp pain point của 85% học viên, giảm từ 90 phút loay hoay buổi chiều xuống 15 phút tự tin buổi sáng.

## §3. Giải pháp tương tự đã nghiên cứu
- **Khanmigo / Codecademy AI**: Flow gợi ý từng dòng code / Đáng học: Chia nhỏ step tương tác / Đáng né: Phụ thuộc vào platform đóng / Mình khác gì: AI Agent tự sinh Mini Codelab bám sát slide giảng viên và repo thực tế của buổi học.
- **NotebookLM**: Flow tổng hợp từ tài liệu / Đáng học: Trích dẫn nguồn Slide/Transcript chính xác / Đáng né: Không có môi trường chạy code tương tác / Mình khác gì: Đưa trích dẫn Slide trực tiếp vào khung code sandbox và quiz củng cố.

## §4. Thiết kế
- **Lát cắt MỘT CÂU**: Học viên VLearn xem và thực hành bài Mini Codelab 15 phút do AI Agent tự động sinh từ slide buổi sáng và repo buổi chiều để hiểu bản chất luồng code trước khi vào bài lab chính.
- **Non-goals (≥3 thứ KHÔNG build)**:
  1. Không xây dựng trình biên dịch Python đầy đủ phía server (dùng browser sandbox execution & simulation).
  2. Không thay thế bài Lab 4 tiếng buổi chiều (chỉ làm mini bridge 15 phút).
  3. Không lưu trữ cơ sở dữ liệu học viên phức tạp (chỉ dùng state client-side cho prototype CP2).
- **Mức prototype nhắm tới**: [x] Mock — Flow bấm được trọn vẹn 2 role (Học viên & Lab Coach), AI Generator thật ở lõi.
- **Automation**: [x] conditional — AI Agent tự động sinh Mini Codelab từ tài liệu, Lab Coach duyệt/điều chỉnh trước khi phát hành (sai thì sửa rẻ).
- **§4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR)**:
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | **G1 — Làm rõ hệ thống làm được gì** | Header & Banner ghi rõ phạm vi: Mini Codelab 15 phút hỗ trợ cầu nối bài lab chiều. |
  | **G2 — Làm rõ nó làm tốt đến đâu** | Trích dẫn rõ nguồn Slide [T04-032] đi kèm từng bước trong Mini Codelab. |
  | **G10 — Thu hẹp phạm vi khi nghi ngờ** | Khi AI Agent phát hiện câu hỏi ngoài bài học hoặc câu hỏi không có căn cứ, Agent từ chối đoán và hiển thị Guardrail. |
  | **G9 — Sửa dễ dàng** | Cho phép Học viên reset code sandbox bất kỳ lúc nào và Lab Coach điều chỉnh prompt rule trước khi sinh bài. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8)
| Tình huống cụ thể | Lớp chỗ khó | Hành vi mong muốn (nói gì, hiện gì, cho user làm gì tiếp) | Nguyên tắc áp |
|---|---|---|---|
| 1. User hỏi thông tin không có trong slide | ① Nguồn sự thật | Báo rõ không tìm thấy trong tài liệu [Txx-NNN] và từ chối bịa | G10 |
| 2. Prompt gõ thiếu thư viện quy định | ② Mơ hồ / thiếu thông tin | Cảnh báo thiếu thư viện theo Constraint Policy và gợi ý bổ sung | G10 |
| 3. User yêu cầu làm hộ toàn bộ bài lab chiều | ③ Ngoài phạm vi / thẩm quyền | Từ chối làm hộ, nhắc nhở đây là Mini Lab 15 phút củng cố lý thuyết | G1 / G10 |
| 4. AI gen code sai cú pháp Python | ④ Đặc thù domain | Hiển thị lỗi Syntax Error rõ ràng trong console và gợi ý sửa | G9 |
| 5. ReAct Agent bị lặp vòng gọi tool | ① Nguồn sự thật | Giới hạn tối đa 3 vòng lặp và ngắt an toàn | G10 |
| 6. User nhập API Key không hợp lệ | ② Mơ hồ / thiếu thông tin | Báo lỗi API Key và tự động fallback sang Agent Engine giả lập | G8 |
| 7. User gõ prompt yêu cầu tư vấn chứng khoán | ③ Ngoài phạm vi / thẩm quyền | Hệ thống kích hoạt System Guardrail từ chối an toàn | G10 |
| 8. Quiz chấm sai đáp án của học viên | ④ Đặc thù domain | Hiển thị giải thích chi tiết đáp án đúng đính kèm căn cứ slide | G11 |

## §6. Bốn đường đi của trải nghiệm
- **Happy path**: Học viên mở VLearn ➔ Chọn Mini Lab buổi sáng ➔ Đọc Slide Bridge ➔ Chạy thử Code ReAct ➔ Trả lời Quiz ➔ Tự tin vào bài lab chiều.
- **Low-confidence (②)**: Input thiếu thông tin ➔ System gợi ý khung code mẫu và prompt quy định.
- **Failure/không căn cứ (①)**: Tra cứu không có tài liệu ➔ HAX G10 kích hoạt từ chối an toàn.
- **Correction (user sửa)**: Học viên thay đổi code/prompt ➔ Bấm "Chạy Mini Agent" để kiểm tra lại log console.
- **Khi bị đòi ngoài phạm vi (③)**: Từ chối ôn tồn và hướng dẫn quay lại bài học.
- **Case đặc thù domain (④)**: Cảnh báo cú pháp và ràng buộc thư viện được hiển thị tức thì.

## §7. Kiểm thử
- **Chiều chất lượng + định nghĩa kiểm chứng được**:
  1. Tính chính xác tài liệu: 100% bước Mini Lab có trích dẫn mã đoạn Slide [Txx-NNN].
  2. Thời gian hoàn thành: Học viên hoàn thành trong ≤15 phút.
  3. Độ an toàn: 100% case ngoài phạm vi kích hoạt HAX G10 thành công.
- **Golden set (≥20 case trong eval/)**: Gồm 10 case lấy từ chatlog thật + 4 case chỗ khó + 6 case bài tập ReAct/HAX.
- **Quality bar**: "Đạt khi ≥ 85% qua bộ eval, và 100% case ngoài phạm vi không bị hallucinate."
- **Kết quả các lượt chạy**: Lượt 1: 90% (18/20 case đạt).

## §8. Phân công & kế hoạch
- **Phân công có tên**:
  - Spec & Evidence: Thành viên Product
  - UI/UX Design & VLearn Aesthetics: Thành viên Frontend
  - AI Agent Generator Engine & Prompting: Thành viên AI Engineer
  - Validation & Demo Script: Thành viên QA & User Test
- **Willing users (≥3 tên/vai)**: Học viên U04, Học viên U12, Lab Coach M02.

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| CP2 | Hoàn thiện Giao diện VLearn 2 Role (Học viên & Lab Coach) | Đáp ứng tiêu chuẩn nộp CP2 bấm trọn flow |
