"""Smoke test cho OpenAI model request-shape.

Mục tiêu: dò nhanh các biến thể payload cho cùng một model cho đến khi tìm ra
biến thể chạy được. Dùng khi một model reasoning như gpt-5.6-luna treo, báo
lỗi temperature, hoặc phản hồi không ổn định.

Chạy:
    python3 openai_model_smoke_test.py gpt-5.6-luna

Mặc định script sẽ thử một vài biến thể an toàn và dừng ở biến thể đầu tiên
thành công. Nếu tất cả thất bại, nó in lỗi chi tiết của từng lượt.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

from dotenv import load_dotenv


def is_reasoning_model_name(model_name: str) -> bool:
    return (model_name or "").startswith(("gpt-5", "o1", "o3", "o4"))


def build_payload(model_name: str, variant: dict) -> dict:
    messages = [
        {
            "role": "developer" if variant.get("developer") else "system",
            "content": "Trả về JSON hợp lệ với các khóa ok, model, variant.",
        },
        {
            "role": "user",
            "content": "Hãy trả về một JSON ngắn với trạng thái kiểm thử.",
        },
    ]

    payload = {
        "model": model_name,
        "messages": messages,
        "response_format": {"type": "json_object"},
    }

    temperature = variant.get("temperature")
    if temperature is not None:
        payload["temperature"] = temperature

    if variant.get("max_completion_tokens") is not None:
        payload["max_completion_tokens"] = variant["max_completion_tokens"]

    if variant.get("reasoning_effort") is not None:
        payload["reasoning_effort"] = variant["reasoning_effort"]

    if variant.get("drop_response_format"):
        payload.pop("response_format", None)

    return payload


def send_request(api_key: str, payload: dict, timeout_seconds: int) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            return 200, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        try:
            body = json.loads(error.read().decode("utf-8"))
            detail = (body.get("error") or {}).get("message") or str(body)
        except Exception:
            detail = error.reason or str(error)
        return error.code, detail
    except urllib.error.URLError as error:
        return 0, str(error.reason)


def candidate_variants(model_name: str) -> list[dict]:
    reasoning = is_reasoning_model_name(model_name)

    if reasoning:
        return [
            {
                "name": "reasoning-default",
                "developer": True,
                "temperature": 1,
                "max_completion_tokens": 256,
                "reasoning_effort": "low",
            },
            {
                "name": "reasoning-no-temperature",
                "developer": True,
                "temperature": None,
                "max_completion_tokens": 256,
                "reasoning_effort": "low",
            },
            {
                "name": "reasoning-no-effort",
                "developer": True,
                "temperature": 1,
                "max_completion_tokens": 256,
                "reasoning_effort": None,
            },
            {
                "name": "reasoning-no-response-format",
                "developer": True,
                "temperature": 1,
                "max_completion_tokens": 256,
                "reasoning_effort": "low",
                "drop_response_format": True,
            },
        ]

    return [
        {
            "name": "standard-low-temp",
            "developer": False,
            "temperature": 0.15,
        },
        {
            "name": "standard-default-temp",
            "developer": False,
            "temperature": 1,
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test OpenAI model payloads")
    parser.add_argument("model", nargs="?", help="Model name, e.g. gpt-5.6-luna")
    parser.add_argument("--timeout", type=int, default=int(os.getenv("OPENAI_HTTP_TIMEOUT_SECONDS", "120")))
    args = parser.parse_args()

    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
    api_key = os.getenv("OPENAI_API_KEY", "")
    model_name = args.model or os.getenv("OPENAI_MODEL") or os.getenv("OPENAI_MODEL_REPO") or "gpt-5.6-luna"

    if not api_key or api_key == "sk-proj-your-openai-api-key-here":
        print("Missing OPENAI_API_KEY in .env", file=sys.stderr)
        return 2

    print(f"Smoke testing model: {model_name}")
    print(f"Reasoning model: {is_reasoning_model_name(model_name)}")

    for index, variant in enumerate(candidate_variants(model_name), start=1):
        payload = build_payload(model_name, variant)
        print(f"Attempt {index}: {variant['name']}", flush=True)
        code, result = send_request(api_key, payload, args.timeout)

        if code == 200:
            choice = result["choices"][0]
            content = choice["message"]["content"]
            print("SUCCESS")
            print(f"finish_reason={choice.get('finish_reason')}")
            print(content)
            return 0

        print(f"HTTP {code}: {result}")

    print("All payload variants failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())