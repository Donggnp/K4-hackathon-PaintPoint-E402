# VLearn Mini Codelab Generator — chạy thử (Nhóm E402)

## Cài đặt (1 lần)
```bash
cd codebase
python3 -m pip install -r requirements.txt
cp ../.env.example ../.env
# Mở .env, dán OPENAI_API_KEY thật vào (sk-proj-...)
```

## Chạy
```bash
python3 server.py
```
Mở trình duyệt: **http://localhost:3000**

Khi khởi động, server tự báo trạng thái:
```
🚀 VLearn Mini Codelab Generator — http://localhost:3000
🐍 Python: /usr/bin/python3
🔑 .env: OPENAI_API_KEY đã nạp
📄 pypdf: sẵn sàng
```
Nếu thấy `❌ pypdf: KHÔNG tìm thấy`, hãy cài bằng **đúng interpreter** mà server in ra ở dòng
`🐍 Python:` — máy có nhiều bản Python là nguyên nhân thường gặp nhất của lỗi này.
Dependency `cryptography` cũng được cài kèm để đọc các PDF dùng mã hoá AES.

---

## Luồng 2 giai đoạn — vai Lab Coach

**Giai đoạn 1 — sinh repo**
1. Vào **👨‍🏫 Lab Coach Studio**. Khung *Tất cả Mini-project* liệt kê mọi bài kèm trạng thái;
   mỗi dòng có nút **🗑️ Xoá**.
2. Ở khung *Tạo Mini-project mới*: chọn **Slide PDF** (PDF có text thật, không phải ảnh scan)
   và **README.md** của bài lab. Không cần nhập URL GitHub, nén hoặc tải lên toàn bộ repo.
3. Bấm **✨ Bước 1 — Sinh repo mini-project** → AI trả về **bản tóm tắt bài lab** + **repo code hoàn chỉnh**.

**Soát và sửa repo**

4. Bấm **🗂️ Mở repo** → File Explorer: cây thư mục bên trái, nội dung file bên phải (có số dòng),
   sửa trực tiếp được. Biểu tượng 🧰 là file có sẵn ở Bước 0, 📄 là file học viên phải tự viết.
5. Hoặc **⬇️ Tải repo (.zip)** về, mở bằng IDE của bạn, chạy `pytest` cho chắc, sửa theo ý,
   rồi **⬆️ Upload repo đã sửa** lên lại.

**Giai đoạn 2 — sinh tutorial**

6. Bấm **✅ Duyệt repo & sinh tutorial**. Chỉ tới lúc này AI mới viết tutorial, và viết
   **từ đúng repo bạn vừa duyệt**.
7. Xem trước, sửa phần chữ nếu cần, rồi **🚀 Duyệt & Phát hành**. Bài mới xuất hiện với học viên.

---

## Vai Học viên

1. Mở bài → **Bước 0**: tải **bộ khung khởi động** (`.zip`) gồm cấu trúc thư mục, file cấu hình
   và **toàn bộ test đã viết sẵn** — không có file logic nào.
2. Dựng `venv`, `pip install -r requirements.txt`, chạy `pytest -q` → thấy test **đỏ**
   (đúng như tutorial báo trước, vì chưa có file logic).
3. Phase 1..N: đọc phần giải thích, **tự gõ code trong IDE của mình**, chạy test cuối mỗi phase
   để thấy từng nhóm test chuyển xanh.
4. Phase cuối: `pytest -q` xanh hết → project hoàn chỉnh.

Cẩm nang chỉ để **đọc** — không có chỗ nào chạy code trên web. Học viên chạy trên máy mình.

---

## Chốt chặn chất lượng

Hệ thống tự động so sánh **từng ký tự** giữa mỗi block code trong tutorial và file tương ứng
trong repo, sau **mọi** thao tác sửa. Còn sai lệch thì **nút Phát hành bị khoá**, kèm nút
*🔧 Đồng bộ tutorial theo repo* để ép nội dung về đúng repo.

Lý do: học viên gõ theo tutorial rồi chạy bộ test có sẵn. Tutorial lệch repo nghĩa là test đỏ
mà học viên không hiểu vì sao — lỗi tệ nhất một app giáo dục có thể mắc.

**Mật độ giải thích** cũng bị kiểm tự động: trong mỗi phase, **cứ 4 dòng code phải có ít nhất
1 dòng giải thích** (1 dòng ≈ 80 ký tự văn xuôi; `checklist` và `quiz` không được tính). Màn duyệt
hiện tỉ lệ `code / giải thích` ngay trên đầu mỗi bước và cảnh báo bước nào còn mỏng.

Hệ thống cũng tự cảnh báo khi: tổng thời lượng ra ngoài khung 30–45 phút, số phase ngoài 5–6,
số file ngoài 10–22, hoặc số dòng logic ngoài 100–200.

---

## API

| Endpoint | Việc |
|---|---|
| `GET /api/status` | Trạng thái API key, model, pypdf |
| `POST /api/generate_repo` | Giai đoạn 1: PDF + README.md → tóm tắt + repo |
| `POST /api/generate_tutorial` | Giai đoạn 2: repo đã duyệt → tutorial |
| `POST /api/pack_repo` | `[{path, content}]` → `.zip` (cả repo, hoặc riêng starter kit qua `only_paths`) |
| `POST /api/unpack_repo` | `.zip` → `[{path, content}]` |
| `POST /api/verify_lab` | Kiểm toàn vẹn tutorial ↔ repo, tính lại thời lượng |

## Lõi AI & vòng tự sửa

Hai giai đoạn có yêu cầu **rất khác nhau**, nên chọn model riêng cho từng cái:

| | Cần gì | Tải đo được (1 bài) | Ghi chú |
|---|---|---|---|
| **GĐ1 — repo** | Suy luận sâu, code đúng liên file, **pass pytest thật** | ~11k vào / ~10–12k ra | Chỗ đáng tiêu tiền |
| **GĐ2 — tutorial** | Viết văn xuôi. Độ chính xác code **không phụ thuộc model** (server tự ép về đúng repo) | ~11–13k vào / **~13–15k ra** | Rẻ hơn được, nhưng cần **trần output lớn** |

```bash
OPENAI_MODEL=gpt-5-mini            # mặc định cho cả hai
# OPENAI_MODEL_REPO=gpt-5          # ghi đè riêng GĐ1 nếu cần mạnh hơn
# OPENAI_MODEL_TUTORIAL=gpt-5-mini # GĐ2 giữ model rẻ
```

GĐ1 phải sinh 100–200 dòng logic khớp chính xác với bộ test trong một lượt.
Nếu model thường xuyên phải retry 3 vòng, hãy cân nhắc dùng model mạnh hơn riêng cho GĐ1.

### Quyết định bằng số liệu, không đoán

Mỗi lần sinh, hệ thống hiện token thật đã tiêu ngay trong màn duyệt:

```
📊 gpt-5-mini · 2 vòng · vào 23,104 token · ra 21,880 token · tổng 44,984
```

Cách dùng: chạy thử 3–5 bài, xem `rounds` trong `auditLog`.
- Thường **1 vòng** → model đang thừa sức, thử hạ xuống bậc rẻ hơn.
- Thường **2–3 vòng** → nâng model cho GĐ1. Nâng model **rẻ hơn** là retry nhiều lần.
- **Hết 3 vòng vẫn fail** → model quá yếu cho việc này, bắt buộc phải nâng.

Các ràng buộc của lớp không chỉ nằm trong prompt — server **đo bằng máy rồi bắt lõi sửa**
(tối đa 3 vòng, đúng §8 spec):

| Giai đoạn | Đo những gì |
|---|---|
| 1 — repo | số file 10–22 · 100–200 dòng logic · cú pháp Python hợp lệ · có `tests/`, `src/`, `pytest.ini`, `requirements.txt` · có package con lồng nhau · không còn TODO/FIXME · **quét bảo mật** · **CHẠY THẬT `pytest`, phải pass 100%** |
| 2 — tutorial | có Bước 0 và Bước 0 không dạy file logic · 5–6 phase · **trùng khít repo từng ký tự** · **tỉ lệ giải thích ≥ 1/4** · có quiz |

Vi phạm được **gửi ngược lại cho lõi kèm lệnh sửa**. Nếu sau 3 vòng vẫn chưa đạt, hệ thống
**không im lặng cho qua** — nó hiện banner đỏ nêu rõ còn vi phạm gì để Coach tự xử lý.

Server cũng bắt trường hợp lõi bị **cắt giữa chừng do chạm trần output** (`finish_reason=length`)
và báo đúng bản chất, thay vì để lỗi vỡ ở bước parse JSON.

### Test-runner — chạy thật, không phải hứa

Sau khi lõi sinh repo, server **ghi repo ra thư mục tạm và chạy `pytest` thật** trong đó.
Test đỏ → traceback nguyên văn được gửi ngược lại cho lõi bắt sửa.

Trước khi chạy, code bị **quét tĩnh bằng `ast`** (chỉ đọc cây cú pháp, không thực thi). Bị chặn:
import `subprocess`/`socket`/`shutil`/`requests`/`urllib`/`ctypes`/`pickle`…, gọi
`eval`/`exec`/`compile`/`os.system`/`os.remove`…, và mở file ở chế độ ghi.
**Có vi phạm bảo mật thì tuyệt đối không chạy.**

Bảo vệ khi chạy: thư mục tạm cô lập, biến môi trường tối giản (không rò `OPENAI_API_KEY`),
timeout **60 giây** rồi `SIGKILL` cả nhóm tiến trình, dọn thư mục tạm dù thành công hay lỗi.

> ⚠️ Đây là **phòng thủ nhiều lớp, không phải sandbox thật**. Muốn an toàn tuyệt đối phải chạy
> trong container/VM riêng. Tắt bằng `VLEARN_RUN_TESTS=0` trong `.env` nếu cần.

Coach có nút **🧪 Chạy lại test** để kiểm lại sau khi tự sửa repo trong File Explorer.

## Dạy lõi làm tốt — không chỉ ra lệnh cho nó

Ràng buộc suông không đủ để một model viết đúng 100–200 dòng code khớp bộ test. System
prompt vì vậy **dạy phương pháp và cho xem mẫu**:

- **Quy trình bắt buộc**: chọn khái niệm → thiết kế 5 tầng → **viết test trước** (test là đặc tả)
  → viết code → **tự chạy lại từng assert trong đầu, tính tay giá trị thật**.
- **Ví dụ vàng nhúng thẳng vào prompt**: trích từ repo đã pass 100% test, để lõi bắt chước giọng
  văn, cách đặt tên, docstring "vì sao", và cách viết test bám hằng số cấu hình.
- **8 luật viết test** chống sai và chống flaky: assert giá trị tường minh, sort tất định có khoá
  phụ, cấm `random`/`datetime.now`, bám hằng số thay vì chép số, cho phép tiêm phụ thuộc để
  test không cần file trên đĩa.
- **4 lỗi kinh điển đã xảy ra thật** kèm cách tránh: từ khoá định tuyến quá rộng, ngưỡng chính
  sách tự mâu thuẫn, `round()` in ra `1e-06`, import đặt cuối file.
- **Tutorial**: một phase mẫu hoàn chỉnh + công thức 7 bước (a→g) + danh sách cú pháp Python
  phải giải thích cho người mới (`default_factory`, dunder, cắt lát âm, `//`, `x or ""`…).
- Nhiệt độ **0.15** cho giai đoạn sinh code — đây là việc phải đúng, không phải viết sáng tạo.

Server tự kiểm prompt lúc khởi động (`📐 prompt: hợp lệ`) — prompt hỏng là lỗi im lặng tệ nhất,
vì lõi vẫn chạy nhưng học sai mẫu.

## Ghi chú
- Dependency thật: `python-dotenv` (đọc `.env`) + `pypdf` (đọc PDF). Gọi OpenAI bằng `urllib` thuần,
  không qua SDK riêng.
- Không có database — mọi mini-project lưu trong state client-side của phiên hiện tại, mất khi reload trang.
  Muốn giữ lại repo thì dùng nút **⬇️ Tải repo (.zip)**.
- Nếu PDF là ảnh scan (không có text layer) hoặc README rỗng, hệ thống dừng và báo lỗi rõ ràng thay vì
  tự đoán (§3.8 Clarification protocol trong `description_tutorial.md`).
- Hai bài mẫu đi kèm (`mini-react-agent` 45 test, `mini-guardrail-pipeline` 36 test) đã được dựng
  và chạy thật: tải `.zip` về chạy `pytest` là pass 100%.
