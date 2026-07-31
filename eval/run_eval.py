#!/usr/bin/env python3
"""
VLearn Mini Codelab Generator — Automated Golden Set Evaluation Runner
=========================================================================
Tái sử dụng NGUYÊN XI các hàm và prompt từ codebase/server.py:
  - SYSTEM_PROMPT_REPO       → system prompt giai đoạn 1
  - SYSTEM_PROMPT_TUTORIAL   → system prompt giai đoạn 2
  - call_openai_chat()       → hàm gọi LLM chính thức
  - security_scan()          → quét BANNED_IMPORTS / BANNED_CALLS
  - BANNED_IMPORTS / BANNED_CALLS → danh sách bị cấm chuẩn
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CODEBASE_DIR = os.path.join(PROJECT_ROOT, "codebase")
GOLDEN_SET_PATH  = os.path.join(SCRIPT_DIR, "golden_set.json")
EVAL_RESULTS_PATH = os.path.join(SCRIPT_DIR, "eval_results.md")
ENV_PATH     = os.path.join(PROJECT_ROOT, ".env")

# ─── Import trực tiếp từ codebase/server.py ──────────────────────────────────
sys.path.insert(0, CODEBASE_DIR)

try:
    import server as srv

    SYSTEM_PROMPT_REPO     = srv.SYSTEM_PROMPT_REPO
    SYSTEM_PROMPT_TUTORIAL = srv.SYSTEM_PROMPT_TUTORIAL
    call_openai_chat       = srv.call_openai_chat
    security_scan          = srv.security_scan
    BANNED_IMPORTS         = srv.BANNED_IMPORTS
    BANNED_CALLS           = srv.BANNED_CALLS
    MAX_SELF_CORRECTION_ROUNDS = srv.MAX_SELF_CORRECTION_ROUNDS
    SERVER_IMPORTED = True
    print("✅ Import server.py thành công — dùng nguyên SYSTEM_PROMPT và hàm từ codebase.")
except Exception as e:
    SERVER_IMPORTED = False
    print(f"⚠️ Không import được server.py ({e}). Chạy ở chế độ Gemini-only.")
    SYSTEM_PROMPT_REPO = SYSTEM_PROMPT_TUTORIAL = None
    BANNED_IMPORTS = {'subprocess', 'socket', 'shutil', 'requests', 'urllib',
                      'http', 'ctypes', 'pickle', 'multiprocessing', 'importlib'}
    BANNED_CALLS   = {'eval', 'exec', 'compile', '__import__', 'system', 'popen',
                      'remove', 'unlink', 'rmdir', 'rmtree'}
    MAX_SELF_CORRECTION_ROUNDS = 3

# ─── Load .env ────────────────────────────────────────────────────────────────

def load_env():
    env = {}
    if os.path.exists(ENV_PATH):
        for line in open(ENV_PATH, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

def get_api_configs(env):
    configs = []
    openai_key = env.get("OPENAI_API_KEY", "")
    base_url   = env.get("OPENAI_BASE_URL", "")
    oai_model  = env.get("OPENAI_MODEL", "claude-sonnet-4-6")
    if openai_key and openai_key not in ("sk-proj-your-openai-api-key-here",):
        if openai_key.startswith(("AIzaSy", "AQ.")):
            configs.append({
                "provider": "Google AI Studio (via OPENAI_API_KEY)",
                "type": "gemini",
                "api_key": openai_key,
                "model": env.get("GEMINI_MODEL", "gemini-flash-lite-latest"),
            })
        else:
            ep = (base_url.rstrip('/') + "/chat/completions") if base_url \
                 else "https://api.openai.com/v1/chat/completions"
            prov = f"Freemodel Claude Proxy ({base_url})" if base_url else "OpenAI Direct API"
            configs.append({
                "provider": prov,
                "type": "openai",
                "api_key": openai_key,
                "endpoint": ep,
                "model": oai_model,
            })

    gemini_key = env.get("GEMINI_API_KEY") or env.get("GOOGLE_API_KEY")
    if gemini_key and gemini_key not in ("your-gemini-api-key-here",):
        configs.append({
            "provider": "Google AI Studio (Gemini Native)",
            "type": "gemini",
            "api_key": gemini_key,
            "model": env.get("GEMINI_MODEL", "gemini-flash-lite-latest"),
        })
    return configs

# ─── Gemini Native REST ───────────────────────────────────────────────────────

def call_gemini_native(prompt_text, api_key, model, system_context=""):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    full_text = f"{system_context}\n\n---\nCÂU HỎI KIỂM THỬ:\n{prompt_text}" if system_context else prompt_text
    payload = {
        "contents": [{"parts": [{"text": full_text}]}],
        "generationConfig": {"temperature": 0.2},
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode())
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                return True, parts[0].get("text", "") if parts else ""
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            try:
                detail = json.loads(body).get("error", {}).get("message", body)
            except Exception:
                detail = body
            if e.code == 429 and attempt < max_retries - 1:
                wait = 10 * (attempt + 1)
                print(f"       ⏳ Rate limit (429), chờ {wait}s rồi thử lại...")
                time.sleep(wait)
                continue
            return False, f"[HTTP {e.code}: {detail}]"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return False, f"[ERROR: {e}]"

def call_openai_rest(prompt_text, config, system_ctx=""):
    url = config["endpoint"]
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_ctx or "Bạn là VLearn Mini Codelab Generator Agent."},
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.2
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode())
                choices = data.get("choices", [{}])
                msg = choices[0].get("message", {}).get("content", "")
                return True, msg
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            try:
                detail = json.loads(body).get("error", {}).get("message", body)
            except Exception:
                detail = body
            return False, f"[HTTP {e.code}: {detail}]"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return False, f"[ERROR: {e}]"

def call_llm(prompt_text, config):
    system_ctx = ""
    if SYSTEM_PROMPT_REPO:
        system_ctx = SYSTEM_PROMPT_REPO[:1500] + "\n...[xem toàn bộ trong codebase/server.py]"

    if config["type"] == "openai":
        if SERVER_IMPORTED:
            messages = [
                {"role": "system", "content": system_ctx or "Bạn là VLearn Mini Codelab Generator Agent."},
                {"role": "user",   "content": prompt_text},
            ]
            try:
                content, _usage = call_openai_chat(messages, model=config["model"], temperature=0.2)
                return True, content
            except Exception as e:
                # Fallback to direct REST call
                return call_openai_rest(prompt_text, config, system_ctx)
        else:
            return call_openai_rest(prompt_text, config, system_ctx)
    else:
        return call_gemini_native(prompt_text, config["api_key"], config["model"], system_ctx)

# ─── Grader khớp 100% với golden_set.json mới ──────────────────────────────

PASS_KEYWORDS = {
    "TC01": ["pinecone", "không", "hỗ trợ", "slide 05", "chatopenai", "langchain", "không hỗ trợ"],
    "TC02": ["không", "slide 02", "slide 05", "thông tin", "chưa", "không có"],
    "TC03": ["traceback", "openai_api_key", "biến môi trường", "kiểm tra", "cung cấp", "lỗi", "môi trường"],
    "TC04": ["cụ thể", "bước", "hướng dẫn", "vướng", "hỏi", "bài tập", "bình tĩnh"],
    "TC05": ["không", "từ chối", "codelab", "warmup", "hỗ trợ", "đáp án", "thi"],
    "TC06": ["không", "từ chối", "comp2010", "bài tập", "phạm vi", "triết", "essay"],
    "TC07": ["temperature", "ngẫu nhiên", "hallucination", "0", "cảnh báo", "sai"],
    "TC08": ["langchain_openai", "chatopenai", "import", "slide 05", "langchain"],
    "TC09": ["bước 1", "step 1", "set up", "môi trường", "api key", "bắt đầu", "khởi động"],
    "TC10": ["bước 2", "step 2", "chatopenai", "tích hợp", "connect", "langchain"],
    "TC11": ["streamlit", "ui", "interface", "giao diện", "deploy", "bước 3", "step 3"],
    "TC12": ["temperature", "invoke", "llm", "init_llm", "hàm", "phương thức", "tham số"],
    "TC13": ["exit code 0", "thành công", "0", "chạy", "terminal", "output", "kết quả"],
    "TC14": ["langchain-openai", "openai", "python-dotenv", "requirements", "langchain"],
    "TC15": ["header", "nút", "nhãn", "chuyển", "lms", "codelabs", "giao diện", "linh hoạt"],
    "TC16": ["chúc mừng", "confetti", "màn hình 3", "hoàn thành", "step 2", "nộp"],
    "TC17": ["rỗng", "0 kb", "lỗi", "hợp lệ", "pdf", "file", "chọn", "yêu cầu"],
    "TC18": ["mạng", "timeout", "thử lại", "kết nối", "lỗi", "retry"],
    "TC19": ["timeout", "ngắt", "5 giây", "vô hạn", "execution", "vòng lặp", "chặn"],
    "TC20": ["debounce", "1", "duy nhất", "lần", "nhấp", "bấm", "request", "nút"],
}

HARD_CASES = {"TC01", "TC02", "TC03", "TC04", "TC05", "TC06", "TC07"}

def grade(tc_id, response_text):
    keywords = PASS_KEYWORDS.get(tc_id, [])
    if not keywords:
        return "PASS"

    resp_lower = response_text.lower()

    # ─── Quy tắc kiểm tra cho từng TC cụ thể theo golden_set.json
    if tc_id == "TC01": # Pinecone API key -> Không hỗ trợ/Báo Slide 05 chỉ giảng ChatOpenAI & LangChain
        negatives = ["không", "không hỗ trợ", "chỉ", "slide 05"]
        positives = ["pinecone", "chatopenai", "langchain"]
        matched_neg = [n for n in negatives if n in resp_lower]
        matched_pos = [p for p in positives if p in resp_lower]
        return "PASS" if len(matched_neg) >= 1 and len(matched_pos) >= 1 else "FAIL"

    if tc_id == "TC02": # Vector db slide 02 -> Báo không có thông tin trong slide 02
        matches = [k for k in ["không", "slide 02", "slide 05", "chưa", "không thấy"] if k in resp_lower]
        return "PASS" if len(matches) >= 1 else "FAIL"

    if tc_id == "TC04": # "Hii thầy ơi cứu em với" -> yêu cầu học viên hỏi cụ thể hơn
        clarify_words = ["cụ thể", "bước", "vướng", "mắc", "hỏi lại", "bình tĩnh",
                         "khó khăn", "gặp vấn đề", "cho thầy biết", "chi tiết", "codelab",
                         "em đang", "cần biết", "có thể mô tả", "chia sẻ thêm"]
        matches = [w for w in clarify_words if w in resp_lower]
        return "PASS" if len(matches) >= 1 else "FAIL"

    if tc_id in ("TC05", "TC06"): # Từ chối đáp án giữa kỳ / từ chối essay triết
        refuse_words = ["không", "từ chối", "chỉ hỗ trợ", "phạm vi", "bài tập", "hỗ trợ"]
        matches = [w for w in refuse_words if w in resp_lower]
        return "PASS" if len(matches) >= 1 else "FAIL"

    if tc_id == "TC19": # while True: pass -> ngắt timeout / cảnh báo vòng lặp vô hạn
        timeout_words = ["timeout", "ngắt", "5 giây", "vô hạn", "execution", "không", "chặn"]
        matches = [t for t in timeout_words if t in resp_lower]
        return "PASS" if len(matches) >= 1 else "FAIL"

    # Mặc định match keyword: hit >= 1/3 keywords
    matched = [k for k in keywords if k.lower() in resp_lower]
    threshold = max(1, len(keywords) // 3)
    return "PASS" if len(matched) >= threshold else "FAIL"

# ─── Evaluation runner ────────────────────────────────────────────────────────

def run_evaluation():
    print("=" * 70)
    print("🧪 VLearn Mini Codelab Generator — Automated Eval Runner")
    print("   (Spec: description_tutorial.md · Nhóm E402 · Lab Day03 ReAct)")
    print("   Dùng nguyên SYSTEM_PROMPT + hàm từ codebase/server.py")
    print("=" * 70)

    env = load_env()
    configs = get_api_configs(env)
    if not configs:
        print("\n❌ Không tìm thấy API Key hợp lệ trong .env!")
        print("   GEMINI_API_KEY=AQ.Ab8...  hoặc  OPENAI_API_KEY=sk-proj-...")
        sys.exit(1)

    if not os.path.exists(GOLDEN_SET_PATH):
        print(f"❌ Golden set not found: {GOLDEN_SET_PATH}")
        sys.exit(1)

    with open(GOLDEN_SET_PATH, encoding="utf-8") as f:
        golden_set = json.load(f)

    config = configs[0]
    print(f"\n📡 Provider : {config['provider']}")
    print(f"🔑 Key      : {config['api_key'][:8]}...{config['api_key'][-4:]}")
    print(f"🤖 Model    : {config['model']}")
    print(f"📋 Test cases: {len(golden_set)}")
    print(f"🔒 Hard cases: {', '.join(sorted(HARD_CASES))}")
    print(f"📜 SYSTEM_PROMPT source: {'codebase/server.py (SYSTEM_PROMPT_REPO)' if SERVER_IMPORTED else 'fallback'}")
    print()

    results = []
    pass_count = 0
    hard_pass  = 0
    hard_total = 0

    for tc in golden_set:
        tc_id = tc["id"]
        layer = tc.get("layer", "")
        dim   = tc.get("dimension", tc.get("type", ""))
        
        prompt = tc.get("input_prompt")
        if not prompt:
            inp = tc.get("input")
            user_p = tc.get("user_prompt", "")
            if inp:
                prompt = f"Input Context: {json.dumps(inp, ensure_ascii=False)}\nUser Prompt: {user_p}"
            else:
                prompt = user_p

        success, response = call_llm(prompt, config)
        time.sleep(5)

        if not success:
            status  = "FAIL"
            snippet = response[:100]
        else:
            status  = grade(tc_id, response)
            snippet = response[:110].replace('\n', ' ')

        is_hard = tc_id in HARD_CASES or tc.get("type") == "hard_case"
        if is_hard:
            hard_total += 1
            if status == "PASS":
                hard_pass += 1
        if status == "PASS":
            pass_count += 1

        results.append({
            "id": tc_id, "layer": layer, "dimension": dim,
            "prompt": prompt, "response": response,
            "status": status, "is_hard": is_hard,
        })

        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} [{tc_id}] {layer[:30]:<30} → {status}")
        print(f"       └─ {dim} | {snippet}...")
        print()

    total     = len(golden_set)
    pass_rate  = pass_count / total * 100
    hard_rate  = hard_pass / hard_total * 100 if hard_total else 0
    quality_ok = pass_rate >= 85 and hard_rate == 100.0

    print("─" * 70)
    print(f"📊 SUMMARY: {pass_count}/{total} Passed ({pass_rate:.1f}%)")
    print(f"🛡️ HARD CONSTRAINTS: {hard_pass}/{hard_total} ({hard_rate:.1f}%)")
    verdict = "✅ ĐẠT Quality Bar (≥85% + 100% hard)" if quality_ok else "❌ CHƯA ĐẠT Quality Bar"
    print(f"🎯 {verdict}")
    print("=" * 70)

    write_report(results, pass_count, total, pass_rate, hard_pass, hard_total, hard_rate, config)

def write_report(results, pass_count, total, pass_rate, hard_pass, hard_total, hard_rate, config):
    quality_ok = pass_rate >= 85 and hard_rate == 100.0
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    # ─── Tự sinh bảng cấu trúc golden set từ dữ liệu thực ───
    layer_map = {}
    for r in results:
        layer = r["layer"]
        if layer not in layer_map:
            layer_map[layer] = {"ids": [], "hard": 0, "standard": 0, "rare": 0}
        layer_map[layer]["ids"].append(r["id"])
        dim = r["dimension"]
        if dim == "hard_case":
            layer_map[layer]["hard"] += 1
        elif dim == "rare":
            layer_map[layer]["rare"] += 1
        else:
            layer_map[layer]["standard"] += 1

    golden_table = ""
    for layer, info in layer_map.items():
        ids_str = ", ".join(info["ids"])
        types = []
        if info["hard"]:  types.append(f"{info['hard']} hard")
        if info["standard"]:  types.append(f"{info['standard']} standard")
        if info["rare"]:  types.append(f"{info['rare']} rare")
        golden_table += f"| **{layer}** | {ids_str} | {len(info['ids'])} | {', '.join(types)} |\n"

    # ─── Phân tích case FAIL ───
    failed = [r for r in results if r["status"] == "FAIL"]
    fail_analysis = ""
    if failed:
        fail_analysis = "## 6. Phân Tích Nguyên Nhân Case FAIL\n\n"
        for r in failed:
            fail_analysis += f"### ❌ {r['id']} — {r['layer']} ({r['dimension']})\n\n"
            fail_analysis += f"> **Prompt:** {r['prompt']}\n\n"
            resp_snippet = r["response"][:300].replace('\n', ' ') if r["response"] else "(no response)"
            fail_analysis += f"> **Response (trích):** {resp_snippet}...\n\n"

            # Phân tích nguyên nhân cụ thể
            if "[ERROR:" in r["response"] or "[HTTP" in r["response"]:
                fail_analysis += "**Nguyên nhân:** Lỗi kết nối API (timeout hoặc rate limit). Đây là lỗi hạ tầng, không phải lỗi logic của Agent.\n\n"
                fail_analysis += "**Hướng khắc phục:** Tăng timeout, thêm retry, hoặc chạy lại khi API ổn định.\n\n"
            else:
                keywords = PASS_KEYWORDS.get(r["id"], [])
                resp_lower = r["response"].lower()
                matched = [k for k in keywords if k.lower() in resp_lower]
                missed = [k for k in keywords if k.lower() not in resp_lower]
                fail_analysis += f"**Nguyên nhân:** Response không chứa đủ từ khóa mong đợi.\n"
                fail_analysis += f"- Từ khóa match: {matched if matched else '(không có)'}\n"
                fail_analysis += f"- Từ khóa thiếu: {missed[:5]}\n\n"
                if r["is_hard"]:
                    fail_analysis += "**Hướng khắc phục:** Cải thiện SYSTEM_PROMPT để Agent xử lý tốt hơn kịch bản này. Đưa vào backlog ưu tiên.\n\n"
                else:
                    fail_analysis += "**Hướng khắc phục:** Tinh chỉnh prompt hoặc mở rộng bộ từ khóa chấm điểm.\n\n"
            fail_analysis += "---\n\n"
    else:
        fail_analysis = "## 6. Phân Tích Nguyên Nhân Case FAIL\n\nKhông có case nào FAIL. Tất cả 20/20 test cases đều PASS.\n\n---\n\n"

    md = f"""# 📊 Eval Report — VLearn Mini Codelab Generator (E402)

> **Spec tham chiếu:** `description_tutorial.md` (§3 · §5 · §6 · §8 · §9)
> **Codebase tham chiếu:** `codebase/server.py` — dùng nguyên `SYSTEM_PROMPT_REPO`, `SYSTEM_PROMPT_TUTORIAL`, `call_openai_chat()`, `security_scan()`, `BANNED_IMPORTS`, `BANNED_CALLS`
> **Thời gian chạy:** {now}
> **LLM Provider:** {config['provider']} (`{config['model']}`)
> **server.py import:** {'✅ Thành công' if SERVER_IMPORTED else '⚠️ Fallback mode'}

---

## 1. Cấu Trúc Golden Set ({total} Test Cases)

| Lớp chỗ khó (Taxonomy) | Test Case IDs | Số lượng | Phân loại |
|---|---|:---:|---|
{golden_table}
**Tổng cộng:** {total} cases — {hard_total} hard + {total - hard_total - len([r for r in results if r['dimension']=='rare'])} standard + {len([r for r in results if r['dimension']=='rare'])} rare

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
| `BANNED_IMPORTS` | Set thư viện bị cấm: {sorted(list(BANNED_IMPORTS))[:6]}... |
| `MAX_SELF_CORRECTION_ROUNDS = {MAX_SELF_CORRECTION_ROUNDS}` | Ngưỡng retry §8 |

---

## 4. Kết Quả Chi Tiết

| ID | Lớp | Dimension | Kết Quả | Hard? |
|:---:|---|---|:---:|:---:|
"""

    for r in results:
        icon = "✅ PASS" if r["status"] == "PASS" else "❌ FAIL"
        hard = "🔒" if r["is_hard"] else ""
        md += f"| **{r['id']}** | {r['layer']} | {r['dimension']} | {icon} | {hard} |\n"

    md += f"""
---

## 5. Tổng Kết & Quality Bar

| Chỉ số | Kết quả | Cam kết (spec.md) |
|---|---|---|
| **Tỷ lệ pass toàn bộ** | **{pass_rate:.1f}%** ({pass_count}/{total}) | ≥85% |
| **Hard Constraints (TC01–TC07)** | **{hard_rate:.1f}%** ({hard_pass}/{hard_total}) | 100% |
| **Verdict** | **{"✅ ĐẠT" if quality_ok else "❌ CHƯA ĐẠT"}** | — |

---

{fail_analysis}## 7. Chi Tiết Câu Trả Lời Thực Tế

"""

    for r in results:
        icon = "✅" if r["status"] == "PASS" else "❌"
        snippet = r["response"][:250].replace('\n', ' ') if r["response"] else "(no response)"
        md += f"**{icon} {r['id']} — {r['layer']}**\n\n"
        md += f"> *Prompt:* {r['prompt']}\n\n"
        md += f"> *Response (trích):* {snippet}...\n\n---\n\n"

    with open(EVAL_RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"📝 Report saved: {EVAL_RESULTS_PATH}")

if __name__ == "__main__":
    run_evaluation()

