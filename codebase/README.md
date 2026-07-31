# VLearn Mini Codelab Generator — chạy thử (Nhóm E402)

## Cấu trúc thư mục

```
codebase/
├── run.py                  ← chạy cái này để khởi động server
├── requirements.txt
├── vlearn/                 ← backend, tách theo mối quan tâm
│   ├── history.py            lưu lịch sử lượt sinh ra đĩa
│   ├── jobs.py               chạy việc nặng ở luồng nền + báo tiến độ
│   ├── tutorial_builder.py   sinh tutorial theo từng phase, SONG SONG
│   ├── config.py             hằng số, nạp .env, chọn model
│   ├── extractors.py         đọc slide PDF / repo .zip / README.md
│   ├── packaging.py          đóng-mở gói .zip, tách bộ khung khởi động
│   ├── openai_client.py      biên giới DUY NHẤT với OpenAI
│   ├── prompts/              system prompt 2 giai đoạn (kèm ví dụ vàng)
│   ├── security.py           quét tĩnh code do lõi sinh
│   ├── testrunner.py         chạy thật pytest trong thư mục tạm
│   ├── quality.py            đo toàn vẹn, mật độ giải thích, thời lượng
│   ├── auditors.py           chấm bài lõi bằng tiêu chí đo được
│   ├── pipeline.py           vòng sinh → chấm → bắt sửa
│   └── http_api.py           định tuyến HTTP (mỏng)
├── web/                    ← giao diện, không cần bundler
│   ├── index.html
│   ├── css/styles.css
│   └── js/
│       ├── seed-data.js      2 bài mẫu đã chạy pytest thật
│       ├── core/             state, utils, quality, timer, transfer
│       ├── views/            shell, student, coach, explorer, workspace
│       ├── actions.js        vòng đời mini-project
│       └── main.js           khởi động
└── tools/
    └── openai_model_smoke_test.py
```

## Cài đặt (1 lần)
```bash
cd codebase
python3 -m pip install -r requirements.txt

# BẮT BUỘC: dựng ảnh sandbox để chạy test của repo do AI sinh ra.
# (server cũng tự dựng lúc khởi động nếu thấy Docker mà chưa có ảnh)
docker build -t vlearn-sandbox:1 sandbox
cp ../.env.example ../.env
# Mở .env, dán OPENAI_API_KEY thật vào (sk-proj-...)
```

## Chạy
```bash
python3 run.py
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

---

## Luồng 2 giai đoạn — vai Lab Coach

**Giai đoạn 1 — sinh repo**
1. Vào **👨‍🏫 Lab Coach Studio**. Lần đầu vào, danh sách **trống** — không có bài mẫu nào lẫn vào.
   Khung *Tất cả Mini-project* liệt kê bài bạn tạo kèm trạng thái; mỗi dòng có nút **🗑️ Xoá**.
2. Ở khung *Tạo Mini-project mới*: chọn **Slide PDF** buổi sáng (PDF có text thật, không phải ảnh scan),
   rồi mô tả lab buổi chiều theo **một trong hai cách**:
   - **📄 README.md** *(mặc định)* — chọn file `.md` hoặc dán thẳng nội dung. Nhẹ, nhanh, và
     thường là đủ: lõi chỉ cần biết lab chiều **làm gì**, dùng công nghệ gì, kiến trúc ra sao.
   - **📦 Cả repo (.zip)** — nhiều ngữ cảnh nhất, nhưng file có thể rất nặng. Hệ thống tự lọc
     `node_modules`/`venv`/`.git` và chỉ đọc file tree + file cốt lõi.
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

Nếu muốn dò riêng model GPT-5.6 / reasoning model khi thấy bị pending, chạy:

```bash
python3 tools/openai_model_smoke_test.py gpt-5.6-luna
```

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
số file ngoài 10–22, hoặc số dòng logic ngoài 400–600.

---

## API

| Endpoint | Việc |
|---|---|
| `GET /api/status` | Trạng thái API key, model, pypdf |
| `POST /api/generate_repo` | Giai đoạn 1: PDF + (`source_kind: readme` hoặc `zip`) → tóm tắt + repo |
| `POST /api/generate_tutorial` | Giai đoạn 2: repo đã duyệt → tutorial |
| `POST /api/pack_repo` | `[{path, content}]` → `.zip` (cả repo, hoặc riêng starter kit qua `only_paths`) |
| `POST /api/unpack_repo` | `.zip` → `[{path, content}]` |
| `POST /api/verify_lab` | Kiểm toàn vẹn tutorial ↔ repo, tính lại thời lượng |
| `GET /api/job/<id>` | Tiến độ của một lượt sinh đang chạy nền |
| `GET /api/runs` | Danh sách lịch sử các lượt đã chạy |
| `GET /api/runs/<id>` | Nạp lại toàn bộ một lượt cũ |
| `POST /api/runs/save` · `POST /api/runs/delete/<id>` | Lưu / xoá một lượt |

`/api/generate_tutorial` trả **409 kèm `needsConfirmation: true`** nếu repo chưa pass hết test.
Gửi lại với `allowFailingTests: true` để xác nhận và tiếp tục. Bài sinh ra được **ghi dấu vĩnh viễn**
`generatedFromFailingTests`, hiện banner nhắc trong màn duyệt và lưu vào lịch sử — Coach có thể
quên, nhưng lịch sử thì không.

## Tốc độ — vì sao nhanh

Bản đầu mất **15+ phút** một lượt và trông như treo. Đã sửa 4 chỗ, đo lại còn
**~50 giây** (repo) + **~27 giây** (tutorial):

1. **Server đa luồng.** `TCPServer` đơn luồng khiến suốt lúc sinh bài, mọi request
   khác đều bị chặn — cả trang đứng hình. Đổi sang `ThreadingHTTPServer`.
2. **Chạy nền + báo tiến độ.** POST trả `jobId` ngay (0.02s), giao diện hỏi
   `/api/job/<id>` mỗi 2 giây và hiện "Vòng 2/3 · 1m 12s" thay vì vòng xoay im lặng.
3. **Hạ SÀN quy mô xuống 200 dòng** (trần vẫn rộng 650). Sàn cao khiến lõi phải sửa
   thêm mấy vòng chỉ để thêm vài chục dòng chẳng dạy thêm gì. Sàn thấp → vòng 1 đạt ngay.
4. **Tutorial sinh theo từng phase, chạy song song.** Một lượt gọi cho cả tutorial mất
   trên 9 phút vì model phải cân cùng lúc: bố cục 6 phase, phủ hết file logic, tỉ lệ
   giải thích, nhịp 7 khối. Giờ tách thành dàn ý → từng phase song song → vá riêng
   phase nào mỏng. Tổng thời gian bằng phase chậm nhất.

5. **Không gửi lại output cũ khi bắt lõi sửa.** Bản đầu nhét nguyên bài vòng 1 (~5.000
   token) vào ngữ cảnh vòng 2 → đầu vào phình gấp đôi, một lượt đội từ 27 giây lên
   **hơn 10 phút rồi timeout**. Giờ chỉ gửi danh sách vi phạm; vòng 2 còn ~30 giây.

Ngoài ra: lõi **không phải chép lại code** nữa. Nó chỉ ghi `filename`, server chèn nội
dung file thật vào. Vừa nhanh hơn, vừa khiến code trong tutorial **không thể** lệch repo.

## Lõi AI & vòng tự sửa

Hai giai đoạn có yêu cầu **rất khác nhau**, nên chọn model riêng cho từng cái:

| | Cần gì | Tải đo được (1 bài) | Ghi chú |
|---|---|---|---|
| **GĐ1 — repo** | Suy luận sâu, code đúng liên file, **pass pytest thật** | ~11k vào / ~10–12k ra | Chỗ đáng tiêu tiền |
| **GĐ2 — tutorial** | Viết văn xuôi. Độ chính xác code **không phụ thuộc model** (server tự ép về đúng repo) | ~11–13k vào / **~13–15k ra** | Rẻ hơn được, nhưng cần **trần output lớn** |

```bash
# Chọn 1 model cho cả hai giai đoạn, hoặc tách riêng từng giai đoạn bên dưới.
OPENAI_MODEL=gpt-5.6-luna

# Nếu muốn tối ưu chi phí/chất lượng theo từng giai đoạn, bật hai dòng này:
# OPENAI_MODEL_REPO=gpt-5
# OPENAI_MODEL_TUTORIAL=gpt-5-mini
```

**Đừng dùng model yếu cho GĐ1**: nó phải sinh 400–600 dòng logic khớp chính xác với ~330 dòng
test trong một lượt. Fail thì retry 3 vòng → tốn gấp 3 lần token mà vẫn có thể hỏng.

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
| 1 — repo | số file 10–22 · 400–600 dòng logic · cú pháp Python hợp lệ · có `tests/`, `src/`, `pytest.ini`, `requirements.txt` · có package con lồng nhau · thiếu `__init__.py` · test import module không tồn tại · dùng `random`/`datetime.now` · không còn TODO/FIXME · **quét bảo mật** · **CHẠY THẬT `pytest` TRONG DOCKER, phải pass 100%** |
| 2 — tutorial | có Bước 0 và Bước 0 không dạy file logic · 5–6 phase · **trùng khít repo từng ký tự** · **tỉ lệ giải thích ≥ 1/4** · **cây thư mục vẽ đúng file có thật** · có quiz |

Vi phạm được **gửi ngược lại cho lõi kèm lệnh sửa**. Nếu sau 3 vòng vẫn chưa đạt, hệ thống
**không im lặng cho qua** — nó hiện banner đỏ nêu rõ còn vi phạm gì để Coach tự xử lý.

Server cũng bắt trường hợp lõi bị **cắt giữa chừng do chạm trần output** (`finish_reason=length`)
và báo đúng bản chất, thay vì để lỗi vỡ ở bước parse JSON.

### Test-runner — chạy thật trong Docker sandbox

Sau khi lõi sinh repo, server **ghi repo ra thư mục tạm rồi chạy `pytest -v` trong một Docker
container cách ly**. Test đỏ → traceback nguyên văn được gửi ngược lại cho lõi bắt sửa, lặp tới
khi xanh hết (tối đa `VLEARN_MAX_FIX_ROUNDS`, mặc định 5 vòng).

**Vì sao bắt buộc Docker?** Code này do một mô hình ngôn ngữ viết ra từ nội dung người ngoài nạp
lên. Quét tĩnh không bao giờ bắt hết được — chỉ cần một cách gọi gián tiếp mà bộ quét chưa biết
là mã độc lọt xuống máy thật. Container cho ranh giới cứng ở tầng hệ điều hành:

```
--network none              không mạng
--read-only                 rootfs chỉ đọc
--tmpfs /tmp                chỗ ghi tạm trong RAM
--memory 512m --cpus 1.0    chặn ngốn tài nguyên
--pids-limit 256            chặn fork bomb
--cap-drop ALL              bỏ mọi quyền đặc biệt
--security-opt no-new-privileges
user runner (không phải root)
```

Đã kiểm chứng bằng test tự động: mã chạy `rm -rf /etc/hostname` **không phá được** hệ thống file
gốc, và `socket.create_connection()` **không ra được mạng**.

**Trước** khi chạy, code còn bị **quét tĩnh bằng `ast`**: chặn import `subprocess`/`socket`/
`shutil`/`requests`/`ctypes`/`pickle`…, chặn `eval`/`exec`/`os.system`/`os.remove`…, chặn mở file
ở chế độ ghi. Có vi phạm bảo mật thì **tuyệt đối không chạy**.

**Nếu máy không có Docker**, hệ thống **từ chối chạy test** thay vì âm thầm chạy trên máy thật.
Muốn chấp nhận rủi ro thì đặt `VLEARN_UNSAFE_HOST_TESTS=1` — báo cáo sẽ gắn cờ đỏ để Coach biết.

### Coach thấy gì trước khi duyệt

- Huy hiệu **🐳 Docker sandbox** xác nhận đã chạy trong container.
- **Tên từng test** kèm dấu ✓/✗ — không chỉ con số tổng.
- Nút **Xem toàn bộ log terminal** mở ra log pytest nguyên văn kèm lệnh `docker run` đã dùng.
- Nếu repo **chưa pass hết test**, nút đổi thành **⚠️ Duyệt dù test chưa xanh** (màu vàng) và
  hệ thống **hỏi lại** trước khi sinh — nêu rõ đang pass mấy/mấy và hậu quả. Coach là người
  quyết định; hệ thống cảnh báo chứ không cấm.
- Nút **🧪 Chạy lại test** để kiểm lại sau khi tự sửa repo trong File Explorer.

### Test cho chính backend

```bash
cd codebase && python3 -m pytest tests/ -v      # 70 test
```

Bao gồm 4 test chạy sandbox thật (tự bỏ qua nếu máy không có Docker).

## Lịch sử lượt chạy — mở lại bất cứ lúc nào

Mỗi lượt sinh được **lưu ra đĩa**, không chỉ nằm trong bộ nhớ trình duyệt (reload trang là
mất trắng). Thư mục lưu ở dạng **đọc được bằng mắt**, không phải một cục JSON:

```
codebase/runs/2026-07-31T13-12-29__mini-react-agent/
├── manifest.json     tóm tắt: thời gian, model, số vòng, token, test pass mấy/mấy
├── lab.json          toàn bộ dữ liệu để nạp lại vào Studio
├── repo/             cây thư mục THẬT — mở IDE, chạy `pytest` được ngay
├── tutorial.md       tutorial dạng Markdown, đọc thẳng không cần app
└── test-output.txt   log pytest nguyên văn của lượt đó
```

Ngay cả khi app hỏng, thư mục này vẫn còn nguyên giá trị.

Trong **Lab Coach Studio**, khung *📚 Lịch sử các lượt đã chạy* hiện:

- huy hiệu trạng thái test: **✅ 45/45 test pass** · **❌ ĐỎ — 27/28** · **⚪ chưa chạy test**,
- giai đoạn (`repo` / `tutorial`), số file, số bước, model, số vòng tự sửa, token đã tiêu,
- cảnh báo chất lượng nếu có,
- nút **↩️ Nạp lại** đưa lượt cũ trở lại Studio (thành bản nháp mới, không đè bài đang làm),
- nút **🗑️ Xoá**.

Lượt được lưu tự động sau khi sinh repo và sau khi sinh tutorial.

## Dạy lõi làm tốt — không chỉ ra lệnh cho nó

Ràng buộc suông không đủ để một model viết đúng 450 dòng code khớp 330 dòng test. System
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
- Nếu PDF là ảnh scan (không có text layer) hoặc ZIP rỗng, hệ thống dừng và báo lỗi rõ ràng thay vì
  tự đoán (§3.8 Clarification protocol trong `description_tutorial.md`).
- Hai bài mẫu đi kèm (`mini-react-agent` 45 test, `mini-guardrail-pipeline` 36 test) đã được dựng
  và chạy thật: tải `.zip` về chạy `pytest` là pass 100%.
