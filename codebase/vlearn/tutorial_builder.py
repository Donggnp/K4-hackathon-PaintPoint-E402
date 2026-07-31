"""Sinh tutorial theo từng phase, chạy SONG SONG.

Vì sao không gọi một cú cho cả tutorial?
Đo thực tế: một lượt sinh trọn tutorial mất trên 9 phút và vẫn chưa xong, vì model
phải giữ trong đầu cùng lúc: bố cục 6 phase, phủ đủ mọi file logic, tỉ lệ giải
thích 1/4 ở từng phase, và nhịp 7 khối. Bài toán càng nhiều ràng buộc đan nhau thì
model càng suy luận lâu.

Cách làm ở đây tách thành việc nhỏ, mỗi việc chỉ có vài ràng buộc:

    1. DÀN Ý   — một lượt gọi nhỏ, quyết định có mấy phase, mỗi phase dạy file nào.
    2. TỪNG PHASE — mỗi phase một lượt gọi riêng, CHẠY SONG SONG. Model chỉ cần lo
       viết cho hay một phase, không phải cân cả bài.
    3. VÁ LẠI  — phase nào giải thích quá mỏng thì sinh lại RIÊNG phase đó, thay vì
       vứt cả tutorial đi làm lại.

Nhờ vậy tổng thời gian ~ thời gian của phase chậm nhất, chứ không phải tổng của
tất cả. Và người dùng thấy tiến độ "Phase 3/6" thay vì một vòng xoay im lặng.
"""

import json
from concurrent.futures import ThreadPoolExecutor

from .config import MAX_PHASES, MIN_PHASES, TUTORIAL_PHASE_WORKERS
from .openai_client import call_openai_chat, parse_json_reply
from .prompts import GOLDEN_PHASE_EXAMPLE
from .quality import measure_step_balance

OUTLINE_PROMPT = f"""Bạn là Trợ lý AI thiết kế bài giảng của VLearn.

Cho một repo mini-project đã được duyệt, hãy lập DÀN Ý cho tutorial dạy học viên
gõ lại repo đó từ đầu. CHỈ lập dàn ý, chưa viết nội dung.

Nguyên tắc chia phase:
- {MIN_PHASES}-{MAX_PHASES} phase (chưa kể Bước 0), đánh số 1..N.
- Mỗi phase = MỘT TẦNG KIẾN TRÚC, dạy 1-3 file logic.
- Thứ tự phải theo chiều phụ thuộc: cấu hình -> hợp đồng/lớp cha -> các cài đặt
  cụ thể -> tầng điều phối -> CLI. Học viên không bao giờ phải dùng thứ chưa viết.
- MỌI file logic được liệt kê phải xuất hiện ĐÚNG MỘT LẦN trong toàn bộ dàn ý.
- File thuộc bộ khung khởi động thì KHÔNG đưa vào phase nào (đã cho sẵn ở Bước 0).

Trả về DUY NHẤT 1 JSON:
{{
  "phases": [
    {{"num": 1, "title": "Phase 1 — <tên tầng>", "files": ["config/settings.py"],
      "teaches": "<một câu: phase này dạy ý kiến trúc gì>"}}
  ]
}}
Ngôn ngữ: tiếng Việt."""


PHASE_PROMPT = """Bạn là Trợ lý AI viết cẩm nang học tập của VLearn (VinUni AI Thực Chiến).

Viết nội dung cho ĐÚNG MỘT phase của tutorial. Người đọc là học viên MỚI, chưa có
nền tảng vững, đang gõ tay lại repo trong IDE của mình.

=== QUY TẮC CỨNG ===
1. ĐỪNG CHÉP LẠI CODE. Với block dạy một file, chỉ ghi "filename" và để
   "content": "". Hệ thống tự chèn nội dung file thật vào. Dồn công sức vào GIẢI THÍCH.
   (Block "bash" thì vẫn ghi lệnh thật.)
2. MẬT ĐỘ GIẢI THÍCH: cứ 4 dòng code thì cần ÍT NHẤT 1 dòng giải thích
   (1 dòng ~ 80 ký tự). Chỉ "text" và "callout" được tính. Phase này dạy {code_lines}
   dòng code, nên cần TỐI THIỂU {required_lines} dòng văn xuôi. Hãy viết đủ.

=== NHỊP BẮT BUỘC ===
  (a) "text" — VÌ SAO cần tầng này. Nêu phương án ngây thơ trước, chỉ ra nó hỏng ở
      đâu, rồi mới giới thiệu cách đúng. Kết bằng "Tạo file <code>đường/dẫn.py</code>:"
  (b) "code" — {{"type":"code","lang":"python","filename":"<đường dẫn>","content":""}}
  (c) "text" — khối "<strong>Đọc lại file trên, từng phần:</strong>" dạng <ul><li>.
      Mỗi <li> gọi TÊN THẬT một hàm/biến trong file rồi nói nó làm gì và VÌ SAO viết
      vậy. ĐÂY LÀ KHỐI QUAN TRỌNG NHẤT.
  (d) "callout" — cái bẫy dễ vấp hoặc lý do thiết kế
  (e) "code" lang "bash" — lệnh chạy test của tầng này
  (f) "callout" variant "success" — OUTPUT MONG ĐỢI chính xác
  (g) "checklist" — 3-4 tiêu chí kiểm chứng được
Lặp (b)(c)(d) cho từng file. Tổng 6-12 block.

=== VIẾT CHO NGƯỜI MỚI ===
- Câu ngắn, tự nhiên, như ngồi cạnh giảng cho một người bạn.
- KHÔNG dùng thuật ngữ chưa định nghĩa; lần đầu xuất hiện phải giải thích bằng lời thường.
- Giải thích luôn cú pháp Python người mới hay vướng khi nó xuất hiện: dataclass,
  field(default_factory=list) và bẫy `tags: list = []`, dunder method, cắt lát chỉ số
  âm và bẫy list[-0:], phép //, f-string, `x or ""` chặn None.
- Luôn trả lời được "vì sao lại làm thế?". Tránh câu rỗng kiểu "đoạn này rất quan trọng".

=== VÍ DỤ VÀNG — MỘT PHASE THẬT. BẮT CHƯỚC NHỊP VÀ GIỌNG NÀY ===
{golden}

{extra_rules}

=== TRẢ VỀ (chỉ 1 JSON) ===
{{"num": {num}, "title": "{title}", "estimatedMinutes": <số>, "blocks": [...]}}

Loại block hợp lệ: text (HTML p/strong/em/code/ul/ol/li/br) · code (lang python|bash)
· tree (items) · callout (variant info|warn|success) · checklist (items) · quiz.
KHÔNG có block chạy code trên web. Ngôn ngữ: tiếng Việt."""


STEP_ZERO_PROMPT = """Bạn là Trợ lý AI viết cẩm nang học tập của VLearn.

Viết BƯỚC 0 của tutorial — bước học viên tải bộ khung khởi động và dựng môi trường.

Nội dung bắt buộc, theo thứ tự:
1. "text" — học viên KHÔNG bắt đầu từ trang giấy trắng. Bộ khung có sẵn cấu trúc thư
   mục, file cấu hình và TOÀN BỘ {test_count} test. Nói rõ VÌ SAO test được cho sẵn:
   test chính là BẢN ĐẶC TẢ, test xanh là bằng chứng khách quan code đúng.
2. "callout" info — bảo bấm nút "⬇️ Tải bộ khung khởi động (.zip)" ngay trên đầu bước,
   giải nén rồi mở bằng IDE.
3. "tree" — cây thư mục sau khi giải nén. CHỈ ĐƯỢC vẽ đúng các file trong danh sách
   bộ khung bên dưới, không thêm file nào khác.
4. "code" bash — python -m venv .venv / activate / pip install -r requirements.txt
5. "code" bash — pytest -q
6. "text" — báo trước SẼ THẤY TEST ĐỎ (ModuleNotFoundError), đó là BÌNH THƯỜNG vì
   chưa có file logic. Mỗi phase sau sẽ làm xanh dần từng nhóm test.
7. "callout" warn — bẫy hay gặp: quên kích hoạt .venv, chạy sai thư mục.
8. "checklist" — 3-4 tiêu chí.

TUYỆT ĐỐI KHÔNG dạy file logic nào ở bước này.

Trả về DUY NHẤT 1 JSON:
{{"num": 0, "title": "Bước 0 — Tải bộ khung khởi động & dựng môi trường",
  "estimatedMinutes": 5, "blocks": [...]}}
Ngôn ngữ: tiếng Việt."""


def _repo_context(lab, paths):
    """Nội dung các file mà phase này dạy, để model có cái mà giải thích."""
    by_path = {f['path']: (f.get('content') or '') for f in (lab.get('repo') or {}).get('files', [])}
    return "\n\n".join(
        f"### FILE: {p}\n```python\n{by_path.get(p, '')}\n```" for p in paths)


def _code_lines(lab, paths):
    by_path = {f['path']: (f.get('content') or '') for f in (lab.get('repo') or {}).get('files', [])}
    return sum(len(by_path.get(p, '').splitlines()) for p in paths)


# Lõi hay đặt sai tên trường: dùng "text"/"body"/"lines" thay cho "content"/"items".
# Không chuẩn hoá thì block render ra TRỐNG TRƠN trên màn hình mà chẳng ai báo lỗi.
_CONTENT_ALIASES = ('content', 'text', 'body', 'html', 'value')
_ITEMS_ALIASES = ('items', 'lines', 'entries', 'list')


def _normalize_block(block):
    """Đưa block về đúng schema, chấp nhận vài cách đặt tên trường phổ biến."""
    kind = block.get('type')

    if kind in ('tree', 'checklist'):
        items = next((block[k] for k in _ITEMS_ALIASES if isinstance(block.get(k), list)), None)
        if items is None:
            raw = next((block[k] for k in _CONTENT_ALIASES if isinstance(block.get(k), str)), '')
            items = [l for l in raw.split('\n') if l.strip()]
        block['items'] = items

    elif kind in ('text', 'callout', 'code'):
        value = next((block[k] for k in _CONTENT_ALIASES if isinstance(block.get(k), str)), None)
        if value is None:
            value = ''
        block['content'] = value

    return block


def _fill_code_blocks(step, by_path):
    """Chuẩn hoá block, rồi chèn nội dung file THẬT vào các block code."""
    for block in step.get('blocks') or []:
        _normalize_block(block)
        if block.get('type') == 'code' and block.get('filename') in by_path:
            block['content'] = by_path[block['filename']]
    return step


def build_outline(lab, model, say):
    say("Đang lập dàn ý các phase…")
    files = (lab.get('repo') or {}).get('files', [])
    kit = set(lab.get('starterKit') or [])
    logic = [f for f in files if f['path'] not in kit]

    user = (
        f"Tên bài: {lab.get('title')}\nRepo: {lab.get('repoName')}\n"
        f"Mục tiêu học: {json.dumps(lab.get('learningGoals') or [], ensure_ascii=False)}\n\n"
        "=== FILE LOGIC HỌC VIÊN PHẢI TỰ GÕ (chia hết vào các phase) ===\n"
        + "\n".join(f"- {f['path']} ({len((f.get('content') or '').splitlines())} dòng)" for f in logic)
        + "\n\n=== BỘ KHUNG KHỞI ĐỘNG (đã cho sẵn, KHÔNG đưa vào phase) ===\n"
        + "\n".join(f"- {p}" for p in sorted(kit))
    )

    raw, usage = call_openai_chat(
        [{"role": "system", "content": OUTLINE_PROMPT}, {"role": "user", "content": user}],
        model=model, temperature=0.2)
    outline = parse_json_reply(raw).get('phases') or []

    # Lõi có thể bỏ sót file. Nhét phần bị sót vào phase cuối còn hơn để học viên
    # gặp một file không bao giờ được dạy.
    covered = {p for ph in outline for p in (ph.get('files') or [])}
    missed = [f['path'] for f in logic if f['path'] not in covered]
    if missed and outline:
        outline[-1].setdefault('files', []).extend(missed)

    return outline, usage


LAST_PHASE_RULES = """=== ĐÂY LÀ PHASE CUỐI — BẮT BUỘC THÊM ===
- một block "code" lang "bash" chạy `pytest -q` toàn bộ, kèm "callout" variant
  "success" ghi ĐÚNG output mong đợi (tổng số test của cả repo là {test_count}),
- một block "text" liệt kê 3-4 lỗi hay gặp kèm cách sửa (chạy sai thư mục, thiếu
  __init__.py, quên dòng nào...),
- một block "text" đối chiếu mini-lab này với repo lab chiều: thành phần nào sẽ
  tái xuất, và ở dạng nào,
- ĐÚNG MỘT block "quiz" hỏi vào Ý THIẾT KẾ (vì sao làm vậy), KHÔNG hỏi mẹo cú pháp:
  {{"type":"quiz","question":"...","options":["A","B","C"],"correct":1,"explanation":"..."}}
"""


def build_phase(lab, phase, model, extra_rules="", is_last=False, test_count=0):
    paths = phase.get('files') or []
    lines = _code_lines(lab, paths)
    required = max(1, -(-lines // 4))

    rules = extra_rules
    if is_last:
        rules = LAST_PHASE_RULES.format(test_count=test_count) + "\n" + extra_rules

    prompt = PHASE_PROMPT.format(
        code_lines=lines, required_lines=required,
        num=phase.get('num'), title=phase.get('title', ''),
        golden=GOLDEN_PHASE_EXAMPLE, extra_rules=rules)

    user = (
        f"Bài: {lab.get('title')}\n"
        f"Phase này dạy ý: {phase.get('teaches', '')}\n\n"
        f"=== NỘI DUNG CÁC FILE PHASE NÀY DẠY ===\n{_repo_context(lab, paths)}"
    )

    raw, usage = call_openai_chat(
        [{"role": "system", "content": prompt}, {"role": "user", "content": user}],
        model=model, temperature=0.3)
    step = parse_json_reply(raw)
    step['num'] = phase.get('num')
    return step, usage


def build_step_zero(lab, model, test_count):
    kit = sorted(lab.get('starterKit') or [])
    prompt = STEP_ZERO_PROMPT.format(test_count=test_count)
    user = (f"Repo: {lab.get('repoName')}\n\n=== BỘ KHUNG KHỞI ĐỘNG ===\n"
            + "\n".join(f"- {p}" for p in kit))

    raw, usage = call_openai_chat(
        [{"role": "system", "content": prompt}, {"role": "user", "content": user}],
        model=model, temperature=0.3)
    step = parse_json_reply(raw)
    step['num'] = 0
    return step, usage


def build_tutorial(lab, model, report=None):
    """Sinh trọn tutorial. Trả về (steps, audit_log)."""
    say = report or (lambda *a, **k: None)
    by_path = {f['path']: (f.get('content') or '') for f in (lab.get('repo') or {}).get('files', [])}
    test_count = ((lab.get('summary') or {}).get('testPlan') or {}).get('total') \
        or (lab.get('testReport') or {}).get('total') or 0

    usages = []
    outline, u = build_outline(lab, model, say)
    usages.append(u)

    total = len(outline) + 1
    say(f"Đang viết {total} bước SONG SONG…", round_no=0, total_rounds=total)

    # Bước 0 và các phase độc lập với nhau -> chạy song song. Tổng thời gian bằng
    # bước chậm nhất, thay vì tổng của tất cả.
    done = {'n': 0}

    def track(fn):
        result = fn()
        done['n'] += 1
        say(f"Đã viết xong {done['n']}/{total} bước…", round_no=done['n'], total_rounds=total)
        return result

    with ThreadPoolExecutor(max_workers=TUTORIAL_PHASE_WORKERS) as pool:
        futures = [pool.submit(track, lambda: build_step_zero(lab, model, test_count))]
        last_num = max((p.get('num') or 0) for p in outline) if outline else 0
        futures += [
            pool.submit(track, (lambda ph: lambda: build_phase(
                lab, ph, model, is_last=(ph.get('num') == last_num), test_count=test_count))(ph))
            for ph in outline
        ]
        results = [f.result() for f in futures]

    steps = []
    for step, u in results:
        usages.append(u)
        steps.append(_fill_code_blocks(step, by_path))
    steps.sort(key=lambda s: s.get('num', 0))

    # Vá riêng phase nào giải thích còn mỏng — không đụng tới phase đã đạt.
    thin = [s for s in steps if s.get('num')
            and (lambda m: m[0] and m[1] < m[2])(measure_step_balance(s))]
    if thin:
        say(f"Đang viết thêm giải thích cho {len(thin)} phase còn mỏng…")
        outline_by_num = {p.get('num'): p for p in outline}
        last_num = max((p.get('num') or 0) for p in outline) if outline else 0
        with ThreadPoolExecutor(max_workers=TUTORIAL_PHASE_WORKERS) as pool:
            futures = {}
            for s in thin:
                ph = outline_by_num.get(s['num'])
                if not ph:
                    continue
                code_lines, explain, required = measure_step_balance(s)
                extra = (f"=== LẦN TRƯỚC BỊ TRẢ LẠI ===\nPhase này mới có {explain} dòng giải "
                         f"thích trong khi cần tối thiểu {required}. Hãy viết khối "
                         f"'Đọc lại file trên, từng phần' đầy đủ hơn: gọi tên THÊM nhiều "
                         f"hàm/biến trong file và giải thích vì sao viết như vậy.")
                futures[pool.submit(build_phase, lab, ph, model, extra,
                                    ph.get('num') == last_num, test_count)] = s['num']
            for fut, num in futures.items():
                try:
                    step, u = fut.result()
                    usages.append(u)
                    steps[[i for i, s in enumerate(steps) if s['num'] == num][0]] = \
                        _fill_code_blocks(step, by_path)
                except Exception:
                    pass          # giữ bản cũ; auditor sẽ báo cho Coach biết

    audit_log = [{
        "round": 1,
        "violations": [],
        "passed": True,
        "usage": {
            "model": model,
            "promptTokens": sum(x.get('promptTokens', 0) for x in usages),
            "completionTokens": sum(x.get('completionTokens', 0) for x in usages),
            "totalTokens": sum(x.get('totalTokens', 0) for x in usages),
            "calls": len(usages),
        },
    }]
    return steps, audit_log
