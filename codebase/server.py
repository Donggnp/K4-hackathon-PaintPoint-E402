import http.server
import socketserver
import os
import sys
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Load environment variables from .env file
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file_path = os.path.join(parent_dir, '.env')
if os.path.exists(env_file_path):
    load_dotenv(env_file_path)
else:
    load_dotenv()

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def call_openai_chat(messages, api_key=None, model=None, temperature=0.7):
    """Call real OpenAI API Chat Completions endpoint"""
    key = api_key or os.getenv('OPENAI_API_KEY')
    selected_model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

    if not key or key == 'sk-proj-your-openai-api-key-here':
        raise ValueError("Chưa cấu hình OPENAI_API_KEY hợp lệ trong file .env hoặc trên giao diện!")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    payload = {
        "model": selected_model,
        "messages": messages,
        "temperature": temperature
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        return res_data['choices'][0]['message']['content']


class VLearnRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        # Endpoint 1: Generate Mini Codelab via Real OpenAI API
        if self.path == '/api/generate_minicodelab':
            self.handle_generate_minicodelab(data)
            return

        # Endpoint 2: Run ReAct Agent via Real OpenAI API
        if self.path == '/api/run_agent':
            self.handle_run_agent(data)
            return

        # Fallback 404 for unknown POST API paths
        self.send_error(404, "API Endpoint Not Found")

    def do_GET(self):
        if self.path == '/api/status':
            key = os.getenv('OPENAI_API_KEY', '')
            has_key = bool(key and key != 'sk-proj-your-openai-api-key-here')
            model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            
            res_data = {
                "status": "ok",
                "has_env_key": has_key,
                "model": model,
                "message": "Real OpenAI API Backend Ready" if has_key else "Missing OPENAI_API_KEY in .env"
            }
            self.send_json_response(res_data)
            return

        super().do_GET()

    def handle_generate_minicodelab(self, data):
        morning_slide = data.get('morning_slide', 'Day 4: ReAct Agent Architecture')
        afternoon_repo = data.get('afternoon_repo', 'github.com/vlearn/day4-research-agent-lab')
        rules = data.get('rules', 'Python < 50 lines, ReAct loop comment')
        user_key = data.get('api_key', '').strip()

        system_prompt = (
            "Bạn là Trợ lý AI thiết kế bài giảng của VLearn (VinUni AI Thực Chiến). "
            "Nhiệm vụ của bạn là sinh 1 bài Mini Codelab 15 phút (gồm 3 bước) nhằm nối liền "
            "lý thuyết slide buổi sáng và bài lab 4 tiếng buổi chiều.\n"
            "Hãy trả về định dạng JSON thuần túy (dạng JSON object) có cấu trúc đúng sau:\n"
            "{\n"
            '  "title": "Tên bài Mini Codelab",\n'
            '  "duration": "15 phút",\n'
            '  "morningTopic": "Tên chủ đề sáng",\n'
            '  "morningSlideRef": "Slide trích dẫn cụ thể [Txx-NNN]",\n'
            '  "afternoonLabTarget": "Tên repo chiều",\n'
            '  "description": "Mô tả ngắn bài mini lab",\n'
            '  "steps": [\n'
            '    {\n'
            '      "num": 1,\n'
            '      "title": "Hiểu Lý thuyết & Cầu nối",\n'
            '      "content": "Đoạn văn HTML giải thích lý thuyết slide và vì sao nó giúp ích bài lab chiều..."\n'
            '    },\n'
            '    {\n'
            '      "num": 2,\n'
            '      "title": "Thử nghiệm Code & Prompt",\n'
            '      "starterCode": "Code Python mẫu minh họa luồng ReAct Agent..."\n'
            '    },\n'
            '    {\n'
            '      "num": 3,\n'
            '      "title": "Kiểm tra & Củng cố (Mini Quiz)",\n'
            '      "quiz": {\n'
            '        "question": "Câu hỏi kiểm tra kiến thức HAX/PAIR?",\n'
            '        "options": ["Đáp án A", "Đáp án B", "Đáp án C"],\n'
            '        "correct": 1,\n'
            '        "explanation": "Giải thích vì sao đúng..."\n'
            '      }\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        user_message = (
            f"Slide sáng: {morning_slide}\n"
            f"Repo lab chiều: {afternoon_repo}\n"
            f"Ràng buộc & Prompt rules: {rules}\n"
            f"Hãy sinh 1 bài Mini Codelab thực tế bằng tiếng Việt."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            raw_response = call_openai_chat(messages, api_key=user_key if user_key else None)
            
            # Clean json output if wrapped in ```json ... ```
            cleaned = raw_response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed_lab = json.loads(cleaned)
            self.send_json_response({"success": True, "lab": parsed_lab, "raw_ai_output": raw_response})

        except Exception as e:
            self.send_json_response({
                "success": False,
                "error": str(e),
                "hint": "Vui lòng thêm OPENAI_API_KEY chuẩn vào file .env hoặc ô nhập API Key trên màn hình."
            }, status=500)

    def handle_run_agent(self, data):
        code_input = data.get('code_input', '')
        user_key = data.get('api_key', '').strip()

        system_prompt = (
            "Bạn là ReAct Agent Runner cho VLearn Sandbox. Hãy phân tích đoạn code/prompt của học viên "
            "và thực thi giả lập với format log ReAct rõ ràng gồm:\n"
            "[THOUGHT] Suy nghĩ của Agent\n"
            "[ACTION] Tên Tool gọi (ví dụ lookup_paper, fetch_doc...)\n"
            "[OBSERVATION] Kết quả tool trả về\n"
            "[FINAL ANSWER] Câu trả lời chốt cho học viên."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Chạy thử đoạn code / prompt này:\n\n{code_input}"}
        ]

        try:
            raw_response = call_openai_chat(messages, api_key=user_key if user_key else None)
            self.send_json_response({"success": True, "output": raw_response})
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, status=500)

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))


if __name__ == "__main__":
    print(f"🚀 Starting VLearn Real OpenAI Server on http://localhost:{PORT}")
    print(f"🔑 .env Status: OPENAI_API_KEY {'loaded' if os.getenv('OPENAI_API_KEY') else 'not found'}")
    print(f"📁 Serving files from: {DIRECTORY}")
    
    with socketserver.TCPServer(("", PORT), VLearnRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            sys.exit(0)
