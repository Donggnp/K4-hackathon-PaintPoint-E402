"""Vòng sinh - chấm - bắt sửa: nơi ràng buộc thật sự có hiệu lực với lõi.

Sinh -> máy chấm -> nếu vi phạm thì gửi nguyên văn lỗi ngược lại kèm lệnh sửa
-> sinh lại, tối đa MAX_SELF_CORRECTION_ROUNDS vòng.
"""

from .config import MAX_SELF_CORRECTION_ROUNDS
from .openai_client import call_openai_chat, parse_json_reply



def generate_with_self_correction(system_prompt, user_message, auditor, build_lab,
                                  temperature=0.4, model=None, report=None):
    """Gọi lõi, tự chấm bằng máy, và bắt lõi SỬA nếu vi phạm ràng buộc.

    Đây là chỗ các ràng buộc trong description_tutorial.md thật sự có hiệu lực:
    prompt chỉ là lời dặn, còn vòng lặp này mới là thứ ép model tuân thủ. Không
    có nó thì mọi con số (400-600 dòng, tỉ lệ giải thích 1/4, trùng khít repo)
    chỉ là mong muốn.

    Trả về (lab, audit_log). audit_log ghi lại từng vòng để Coach thấy lõi đã
    phải sửa những gì — minh bạch chứ không giấu.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    audit_log = []
    lab = None
    problems = []

    # `report` do tầng job truyền vào để đẩy tiến độ lên giao diện. Khi gọi trực
    # tiếp (test, script) thì không có, nên thay bằng hàm rỗng cho gọn.
    say = report or (lambda *a, **k: None)

    for attempt in range(1, MAX_SELF_CORRECTION_ROUNDS + 1):
        print(f"[openai] self-correction round={attempt}", flush=True)
        say(f"Vòng {attempt}: lõi đang viết nội dung…",
            round_no=attempt, total_rounds=MAX_SELF_CORRECTION_ROUNDS)

        raw, usage = call_openai_chat(messages, model=model, temperature=temperature)

        say(f"Vòng {attempt}: đang chấm bài và chạy test trong Docker…",
            round_no=attempt, total_rounds=MAX_SELF_CORRECTION_ROUNDS)
        parsed = parse_json_reply(raw)
        lab = build_lab(parsed)
        problems = auditor(lab)

        audit_log.append({
            "round": attempt,
            "violations": problems,
            "passed": not problems,
            "usage": usage,
        })

        if not problems:
            say(f"Đạt mọi ràng buộc sau {attempt} vòng.", round_no=attempt)
            return lab, audit_log

        say(f"Vòng {attempt}: còn {len(problems)} vi phạm, đang bắt lõi sửa…",
            round_no=attempt, detail=problems[:3])

        if attempt == MAX_SELF_CORRECTION_ROUNDS:
            break

        # KHÔNG gửi lại toàn bộ output cũ. Đo được: làm vậy khiến đầu vào vòng 2
        # phình gấp đôi và lượt sinh đội từ 27 giây lên hơn 10 phút. Model chỉ cần
        # biết SAI Ở ĐÂU, không cần đọc lại nguyên bài nó vừa viết.
        messages = messages[:2] + [{
            "role": "user",
            "content": (
                "Lần trước bạn đã sinh một bài nhưng nó VI PHẠM các ràng buộc sau "
                "(đo bằng máy: chạy pytest thật, đếm dòng thật):\n\n"
                + "\n".join(f"{i}. {p}" for i, p in enumerate(problems, start=1))
                + "\n\nHãy sinh LẠI TỪ ĐẦU một bài mới, tránh đúng những lỗi trên. "
                  "Chỉ trả JSON."
            ),
        }]

    # Hết lượt mà vẫn vi phạm: KHÔNG im lặng cho qua, trả về kèm cờ để Coach biết.
    lab['selfCorrectionFailed'] = problems
    return lab, audit_log


def summarize_usage(audit_log):
    """Cộng token của mọi vòng lại.

    Vòng tự sửa khiến chi phí KHÔNG tuyến tính: một model yếu phải sửa 3 vòng sẽ
    tốn gấp ~3 lần một model mạnh làm đúng ngay lần đầu — mà vẫn có thể fail.
    Hiện con số thật để Coach quyết định nâng/hạ model bằng số liệu, không đoán.
    """
    rounds = len(audit_log)
    prompt = sum((r.get('usage') or {}).get('promptTokens', 0) for r in audit_log)
    completion = sum((r.get('usage') or {}).get('completionTokens', 0) for r in audit_log)
    model = next((r.get('usage', {}).get('model') for r in reversed(audit_log)
                  if r.get('usage')), None)
    return {
        "model": model,
        "rounds": rounds,
        "promptTokens": prompt,
        "completionTokens": completion,
        "totalTokens": prompt + completion,
    }
