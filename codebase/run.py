#!/usr/bin/env python3
"""Điểm khởi động server VLearn.

    python3 run.py

Trước khi phục vụ request, script chạy một loạt kiểm tra khởi động. Lý do: mọi
lỗi ở đây (thiếu pypdf, sai tên model, prompt hỏng) đều là loại lỗi im lặng —
server vẫn chạy nhưng cho ra kết quả sai. Thà báo to ngay lúc khởi động còn hơn
để Coach phát hiện sau khi đã ngồi chờ upload xong.
"""

import json
import os
from http.server import ThreadingHTTPServer
import subprocess
import sys

from vlearn.config import (
    DOCKER_IMAGE,
    ENABLE_TEST_RUNNER,
    PORT,
    UNSAFE_ALLOW_HOST_TESTS,
    WEB_DIR,
    model_for,
)
from vlearn.extractors import PdfReader
from vlearn.http_api import VLearnRequestHandler
from vlearn.openai_client import check_model_available
from vlearn.testrunner import build_sandbox_image, docker_status
from vlearn.prompts import GOLDEN_PHASE_EXAMPLE, SYSTEM_PROMPT_REPO
from vlearn.tutorial_builder import OUTLINE_PROMPT, PHASE_PROMPT


def check_pdf_reader():
    if PdfReader is None:
        print("❌ pypdf: KHÔNG tìm thấy — chức năng đọc Slide PDF sẽ lỗi!")
        print(f"   Sửa bằng: {sys.executable} -m pip install -r requirements.txt")
    else:
        print("📄 pypdf: sẵn sàng")


def check_test_runner():
    """Sandbox Docker là điều kiện BẮT BUỘC để chạy mã do AI sinh ra."""
    if not ENABLE_TEST_RUNNER:
        print("⚠️  test-runner: ĐANG TẮT (VLEARN_RUN_TESTS=0) — repo AI sinh không được kiểm hành vi")
        return

    st = docker_status()

    if st['available'] and st['image_ready']:
        print(f"🐳 sandbox: sẵn sàng (Docker {st.get('version', '?')}, ảnh {DOCKER_IMAGE})")
        return

    if st['available'] and not st['image_ready']:
        print(f"🐳 sandbox: Docker chạy nhưng chưa có ảnh '{DOCKER_IMAGE}' — đang dựng...")
        ok, msg = build_sandbox_image()
        print(f"   {'✅' if ok else '❌'} {msg}")
        if ok:
            return

    print(f"❌ sandbox: KHÔNG dùng được — {st['reason']}")
    if UNSAFE_ALLOW_HOST_TESTS:
        print("   ⚠️  VLEARN_UNSAFE_HOST_TESTS=1: sẽ chạy test TRỰC TIẾP trên máy thật.")
        print("      Mã do AI sinh chỉ còn quét tĩnh bảo vệ. Chỉ nên dùng khi bạn hiểu rủi ro.")
    else:
        print("   Hệ thống sẽ TỪ CHỐI chạy test (không chạy mã không đáng tin trên máy thật).")
        print(f"   Sửa bằng: bật Docker rồi `docker build -t {DOCKER_IMAGE} codebase/sandbox`")


def check_prompts():
    """Prompt hỏng là lỗi im lặng tệ nhất: lõi vẫn chạy nhưng học sai mẫu."""
    try:
        json.loads(GOLDEN_PHASE_EXAMPLE)
        assert "{GOLDEN}" not in SYSTEM_PROMPT_REPO
        assert "ToolResult" in SYSTEM_PROMPT_REPO
        phase = PHASE_PROMPT.format(code_lines=1, required_lines=1, num=1, title='x',
                                    golden=GOLDEN_PHASE_EXAMPLE, extra_rules='')
        assert "Đọc lại file trên" in phase
        print(f"📐 prompt: hợp lệ (repo {len(SYSTEM_PROMPT_REPO) // 4} token, "
              f"dàn ý {len(OUTLINE_PROMPT) // 4} token, phase {len(phase) // 4} token)")
    except Exception as e:
        print(f"❌ PROMPT HỎNG: {e} — lõi sẽ học sai mẫu, hãy sửa trước khi dùng!")


def check_models():
    for stage in ('repo', 'tutorial'):
        name = model_for(stage)
        label = 'giai đoạn 1 (repo)    ' if stage == 'repo' else 'giai đoạn 2 (tutorial)'
        print(f"🤖 Lõi — {label}: {name}  {check_model_available(name)}")


def main():
    print(f"🚀 VLearn Mini Codelab Generator — http://localhost:{PORT}")
    print(f"🐍 Python: {sys.executable}")
    print(f"🔑 .env: OPENAI_API_KEY {'đã nạp' if os.getenv('OPENAI_API_KEY') else 'KHÔNG tìm thấy'}")

    check_pdf_reader()
    check_test_runner()
    check_prompts()
    check_models()
    print(f"📁 Giao diện tĩnh: {WEB_DIR}")

    try:
        # ThreadingHTTPServer chứ không phải TCPServer: một lượt sinh bài mất
        # vài phút, mà server đơn luồng thì suốt thời gian đó KHÔNG phục vụ được
        # request nào khác — cả trang web đứng hình, người dùng tưởng hỏng.
        httpd = ThreadingHTTPServer(("", PORT), VLearnRequestHandler)
    except OSError as e:
        print(f"\n❌ Không khởi động được server: {e}")
        print(f"   Port {PORT} đang bị tiến trình khác chiếm (có thể là server cũ).")
        print("   Tắt tiến trình đó (Ctrl+C ở terminal cũ) rồi chạy lại.")
        sys.exit(1)

    with httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nĐã dừng server.")
            sys.exit(0)


if __name__ == "__main__":
    main()
