"""Mọi thứ liên quan tới việc gọi OpenAI: dựng payload, gửi, và dịch lỗi.

Tách riêng vì đây là biên giới duy nhất với thế giới bên ngoài. Khi OpenAI đổi
API hay ta đổi nhà cung cấp, chỉ file này phải sửa.
"""

import json
import os
import urllib.error
import urllib.request

from .config import DEFAULT_MODEL, OPENAI_HTTP_TIMEOUT_SECONDS, REASONING_EFFORT



def is_reasoning_model_name(model_name):
    """Nhận diện nhóm model reasoning mới của OpenAI theo tên model."""
    return (model_name or '').startswith(('gpt-5', 'o1', 'o3', 'o4'))


def build_openai_chat_payload(messages, selected_model, temperature):
    """Tạo payload chat completions phù hợp với họ model đang dùng."""
    reasoning_model = is_reasoning_model_name(selected_model)

    request_messages = list(messages)
    if reasoning_model:
        request_messages = [
            {"role": "developer" if m.get('role') == 'system' else m.get('role'), "content": m.get('content')}
            for m in request_messages
        ]

    payload = {
        "model": selected_model,
        "messages": request_messages,
        "response_format": {"type": "json_object"},
    }

    if reasoning_model:
        # Reasoning models của họ gpt-5 thường chỉ chấp nhận temperature mặc định.
        payload["temperature"] = 1
        # Các model reasoning cần trần output rõ ràng hơn để tránh bị cắt giữa chừng.
        payload["max_completion_tokens"] = 16000
        payload["reasoning_effort"] = REASONING_EFFORT
    elif temperature is not None:
        payload["temperature"] = temperature

    return payload


def temperature_supported_error(detail):
    text = (detail or '').lower()
    return 'temperature' in text and (
        'unsupported value' in text or
        'does not support' in text or
        'only the default' in text or
        'only the default (1)' in text
    )




# ---------------------------------------------------------------------------
# Gọi OpenAI
# ---------------------------------------------------------------------------
def call_openai_chat(messages, model=None, temperature=0.4):
    """Gọi lõi sinh nội dung.

    Bài mini-project dài (repo ~11k token, tutorial ~15k token đầu ra) nên rủi
    ro lớn nhất KHÔNG phải model trả lời sai, mà là model bị CẮT giữa chừng vì
    chạm trần output — lúc đó JSON hỏng và lỗi hiện ra rất khó hiểu. Vì vậy ta
    đọc 'finish_reason' và báo đúng bản chất thay vì để nó vỡ ở bước parse.
    """
    key = os.getenv('OPENAI_API_KEY')
    selected_model = model or os.getenv('OPENAI_MODEL', DEFAULT_MODEL)

    print(f"[openai] start model={selected_model}", flush=True)

    if not key or key == 'sk-proj-your-openai-api-key-here':
        raise ValueError("Chưa cấu hình OPENAI_API_KEY hợp lệ trong file .env!")

    def send(payload):
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            method='POST',
        )

        with urllib.request.urlopen(req, timeout=OPENAI_HTTP_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode('utf-8'))

    payload = build_openai_chat_payload(messages, selected_model, temperature)

    try:
        res_data = send(payload)
    except urllib.error.HTTPError as e:
        # OpenAI trả lý do THẬT trong thân phản hồi. Nuốt mất nó rồi chỉ hiện
        # "HTTP Error 404" là kiểu lỗi khiến người dùng ngồi đoán vô ích.
        try:
            body = json.loads(e.read().decode('utf-8'))
            detail = (body.get('error') or {}).get('message') or str(body)
        except Exception:
            detail = e.reason or str(e)

        if e.code == 400 and temperature_supported_error(detail):
            # Một số model reasoning chỉ chấp nhận nhiệt độ mặc định; retry không
            # gửi temperature để backend tự dùng giá trị an toàn.
            retry_payload = build_openai_chat_payload(messages, selected_model, None)
            try:
                res_data = send(retry_payload)
            except urllib.error.HTTPError as retry_e:
                try:
                    retry_body = json.loads(retry_e.read().decode('utf-8'))
                    retry_detail = (retry_body.get('error') or {}).get('message') or str(retry_body)
                except Exception:
                    retry_detail = retry_e.reason or str(retry_e)
                raise RuntimeError(f"OpenAI trả lỗi HTTP {retry_e.code}: {retry_detail}") from None
        else:
            if e.code == 404:
                raise RuntimeError(
                    f"Không tìm thấy model '{selected_model}'. OpenAI báo: {detail}\n"
                    f"Nguyên nhân thường gặp: gõ sai tên model, hoặc tài khoản chưa được cấp quyền dùng model này.\n"
                    f"Hãy sửa OPENAI_MODEL, OPENAI_MODEL_REPO, hoặc OPENAI_MODEL_TUTORIAL trong file .env rồi KHỞI ĐỘNG LẠI server."
                ) from None
            if e.code == 401:
                raise RuntimeError(f"OPENAI_API_KEY không hợp lệ. OpenAI báo: {detail}") from None
            if e.code == 429:
                raise RuntimeError(f"Bị giới hạn tần suất hoặc hết hạn mức. OpenAI báo: {detail}") from None
            raise RuntimeError(f"OpenAI trả lỗi HTTP {e.code}: {detail}") from None
    except TimeoutError as e:
        raise RuntimeError(
            f"OpenAI bị timeout sau {OPENAI_HTTP_TIMEOUT_SECONDS} giây. "
            "Bài sinh repo này có thể quá nặng, hoặc model đang phản hồi chậm. "
            "Thử tăng OPENAI_HTTP_TIMEOUT_SECONDS trong .env, hoặc dùng model mạnh hơn/ít vòng tự sửa hơn."
        ) from None
    except urllib.error.URLError as e:
        reason = getattr(e, 'reason', e)
        if 'timed out' in str(reason).lower():
            raise RuntimeError(
                f"OpenAI bị timeout sau {OPENAI_HTTP_TIMEOUT_SECONDS} giây. "
                "Bài sinh repo này có thể quá nặng, hoặc model đang phản hồi chậm. "
                "Thử tăng OPENAI_HTTP_TIMEOUT_SECONDS trong .env, hoặc dùng model mạnh hơn/ít vòng tự sửa hơn."
            ) from None
        raise RuntimeError(f"Không kết nối được tới OpenAI: {reason}") from None

    usage = res_data.get('usage') or {}
    choice = res_data['choices'][0]
    if choice.get('finish_reason') == 'length':
        raise RuntimeError(
            f"Model '{selected_model}' bị cắt giữa chừng vì chạm trần output. "
            "Bài đang yêu cầu quá dài cho một lượt trả lời. Cách xử lý: giảm quy mô repo "
            "trong ràng buộc, hoặc dùng model có trần output lớn hơn."
        )

    return choice['message']['content'], {
        "model": selected_model,
        "promptTokens": usage.get('prompt_tokens', 0),
        "completionTokens": usage.get('completion_tokens', 0),
        "totalTokens": usage.get('total_tokens', 0),
    }




def check_model_available(model_name):
    """Hỏi OpenAI xem tên model có thật không, NGAY lúc khởi động.

    Gõ sai tên model là lỗi rất dễ mắc (gpt-5o-mini / gpt-4-o / gpt5-mini...).
    Phát hiện lúc khởi động rẻ hơn nhiều so với để nó nổ ra 404 sau khi Coach đã
    ngồi chờ upload slide và repo xong.
    """
    key = os.getenv('OPENAI_API_KEY')
    if not key or key == 'sk-proj-your-openai-api-key-here':
        return '(chưa có API key nên không kiểm được)'

    req = urllib.request.Request(
        f"https://api.openai.com/v1/models/{model_name}",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10):
            return '✅'
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return '❌ KHÔNG TỒN TẠI hoặc tài khoản chưa có quyền — sửa OPENAI_MODEL / OPENAI_MODEL_REPO / OPENAI_MODEL_TUTORIAL trong .env!'
        if e.code == 401:
            return '❌ API key không hợp lệ'
        return f'⚠️ không kiểm được (HTTP {e.code})'
    except Exception:
        return '⚠️ không kiểm được (mạng)'


def parse_json_reply(raw):
    cleaned = raw.strip()
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    if cleaned.startswith('```'):
        cleaned = cleaned[3:]
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start:end + 1])
        raise
