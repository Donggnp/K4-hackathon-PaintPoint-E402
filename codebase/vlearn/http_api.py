"""Tầng HTTP: định tuyến API và phục vụ giao diện tĩnh.

Cố ý mỏng — mọi logic nghiệp vụ nằm ở các module chuyên trách. File này chỉ lo
đọc request, gọi đúng hàm, và trả JSON.
"""

import base64
import http.server
import json
import os

from .auditors import audit_repo, audit_tutorial
from .config import (
    MIN_README_CHARS,
    MIN_SLIDE_CHARS_FOR_VALID_INPUT,
    WEB_DIR,
    model_for,
)
from .extractors import PdfReader, extract_pdf_text, extract_readme_summary, extract_repo_summary
from .packaging import (
    count_logic_lines,
    derive_starter_kit,
    files_to_zip_base64,
    zip_base64_to_files,
)
from .history import delete_run, list_runs, load_run, save_run
from .jobs import create_job, get_job, run_in_background
from .pipeline import generate_with_self_correction, summarize_usage
from .tutorial_builder import build_tutorial
from .prompts import SYSTEM_PROMPT_REPO
from .quality import normalize_lab
from .testrunner import docker_status




class VLearnRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def log_message(self, fmt, *args):
        if '/api/' in (self.path or ''):
            super().log_message(fmt, *args)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length > 0 else '{}'
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if self.path == '/api/runs/save':
            manifest = save_run(data.get('lab') or {}, data.get('stage') or 'published')
            self.send_json_response({"success": bool(manifest), "manifest": manifest},
                                    status=200 if manifest else 500)
            return

        if self.path.startswith('/api/runs/delete/'):
            ok = delete_run(self.path.rsplit('/', 1)[-1])
            self.send_json_response({"success": ok}, status=200 if ok else 404)
            return

        routes = {
            '/api/generate_repo': self.handle_generate_repo,
            '/api/generate_tutorial': self.handle_generate_tutorial,
            '/api/pack_repo': self.handle_pack_repo,
            '/api/unpack_repo': self.handle_unpack_repo,
            '/api/verify_lab': self.handle_verify_lab,
        }
        handler = routes.get(self.path)
        if handler:
            handler(data)
            return

        self.send_error(404, "API Endpoint Not Found")

    def do_GET(self):
        if self.path.startswith('/api/job/'):
            job = get_job(self.path.rsplit('/', 1)[-1])
            if not job:
                self.send_json_response(
                    {"success": False, "error": "Không tìm thấy job (có thể đã hết hạn)."},
                    status=404)
                return
            self.send_json_response({"success": True, "job": job})
            return

        if self.path == '/api/runs':
            self.send_json_response({"success": True, "runs": list_runs()})
            return

        if self.path.startswith('/api/runs/'):
            lab = load_run(self.path.rsplit('/', 1)[-1])
            if not lab:
                self.send_json_response(
                    {"success": False, "error": "Không tìm thấy lượt chạy này."}, status=404)
                return
            self.send_json_response({"success": True, "lab": lab})
            return

        if self.path == '/api/status':
            key = os.getenv('OPENAI_API_KEY', '')
            has_key = bool(key and key != 'sk-proj-your-openai-api-key-here')
            self.send_json_response({
                "status": "ok",
                "has_env_key": has_key,
                "modelRepo": model_for('repo'),
                "modelTutorial": model_for('tutorial'),
                "has_pypdf": PdfReader is not None,
                "sandbox": docker_status(),
                "message": "Backend sẵn sàng" if has_key else "Thiếu OPENAI_API_KEY trong .env",
            })
            return
        super().do_GET()

    # --- Giai đoạn 1 -------------------------------------------------------
    def handle_generate_repo(self, data):
        pdf_b64 = data.get('pdf_base64', '')
        pdf_filename = data.get('pdf_filename', 'slide.pdf')
        rules = data.get('rules', '')

        # Coach có 2 cách mô tả lab buổi chiều:
        #   'zip'    — nạp cả repo, cho lõi nhiều ngữ cảnh nhất nhưng file nặng
        #   'readme' — chỉ nạp README.md, nhẹ hơn nhiều và thường là đủ, vì lõi
        #              chỉ cần biết lab chiều LÀM GÌ chứ không cần đọc từng dòng code
        source_kind = (data.get('source_kind') or 'zip').lower()
        zip_b64 = data.get('zip_base64', '')
        zip_filename = data.get('zip_filename', 'repo.zip')
        readme_text = data.get('readme_text', '')
        readme_b64 = data.get('readme_base64', '')
        readme_filename = data.get('readme_filename', 'README.md')

        if not pdf_b64:
            self.send_json_response({
                "success": False,
                "error": "Thiếu file Slide PDF buổi sáng.",
                "hint": "Slide (.pdf) là bắt buộc — đó là nguồn lý thuyết để lõi bám vào.",
            }, status=400)
            return

        if source_kind == 'readme' and not (readme_text or readme_b64):
            self.send_json_response({
                "success": False,
                "error": "Thiếu nội dung README.md của lab buổi chiều.",
                "hint": "Chọn file README.md, hoặc dán thẳng nội dung vào ô bên dưới.",
            }, status=400)
            return

        if source_kind == 'zip' and not zip_b64:
            self.send_json_response({
                "success": False,
                "error": "Thiếu file ZIP repo lab chiều.",
                "hint": "Chọn file .zip, hoặc chuyển sang chế độ README.md cho nhẹ.",
            }, status=400)
            return

        try:
            print("[repo] received request", flush=True)
            slide_block, pages_used, pages_total = extract_pdf_text(base64.b64decode(pdf_b64))
        except Exception as e:
            self.send_json_response({
                "success": False,
                "error": f"Không đọc được file PDF ({pdf_filename}): {e}",
                "hint": "Kiểm tra PDF có bị hỏng hoặc là ảnh scan không có text layer không.",
            }, status=400)
            return

        if len(slide_block.strip()) < MIN_SLIDE_CHARS_FOR_VALID_INPUT:
            self.send_json_response({
                "success": False,
                "error": f"Slide PDF chỉ trích được {len(slide_block.strip())} ký tự text.",
                "hint": "PDF có thể là ảnh scan (không có text layer) — hãy chọn file khác.",
            }, status=422)
            return

        if source_kind == 'readme':
            try:
                raw = readme_text or base64.b64decode(readme_b64).decode('utf-8', errors='replace')
                repo_block, source_label = extract_readme_summary(raw, readme_filename)
                file_tree, core_used = [], [readme_filename]
            except Exception as e:
                self.send_json_response({
                    "success": False,
                    "error": f"Không đọc được README ({readme_filename}): {e}",
                    "hint": "Hãy dùng file .md dạng text thuần.",
                }, status=400)
                return

            if len(repo_block.strip()) < MIN_README_CHARS:
                self.send_json_response({
                    "success": False,
                    "error": f"README chỉ có {len(repo_block.strip())} ký tự — quá ít để lõi hiểu lab chiều.",
                    "hint": "Hãy dùng README đầy đủ hơn (mục tiêu, kiến trúc, công nghệ dùng), "
                            "hoặc chuyển sang nạp cả repo .zip.",
                }, status=422)
                return
        else:
            try:
                repo_block, file_tree, core_used = extract_repo_summary(base64.b64decode(zip_b64))
                source_label = zip_filename
            except Exception as e:
                self.send_json_response({
                    "success": False,
                    "error": f"Không đọc được file ZIP ({zip_filename}): {e}",
                    "hint": "Kiểm tra file .zip có đúng định dạng zip thật không (không phải rar/7z đổi đuôi).",
                }, status=400)
                return

            if not file_tree:
                self.send_json_response({
                    "success": False,
                    "error": "File ZIP không còn file nào sau khi lọc.",
                    "hint": "Hãy chọn đúng file .zip của repo lab chiều.",
                }, status=422)
                return

        user_message = (
            f"=== Slide_Buoi_Sang ({pdf_filename}, {pages_total} trang, dùng {pages_used} trang có text) ===\n"
            f"{slide_block}\n\n"
            f"=== Lab_Buoi_Chieu ({source_label}) ===\n{repo_block}\n\n"
            f"=== Ràng buộc thêm từ Lab Coach ===\n{rules or '(không có)'}\n\n"
            "Hãy sinh REPO mini-project hoàn chỉnh theo đúng định dạng JSON đã quy định."
        )

        def build(parsed):
            got = ((parsed.get('repo') or {}).get('files')) or []
            got.sort(key=lambda f: f.get('path') or '')
            parsed.setdefault('repo', {})['files'] = got
            parsed['starterKit'] = derive_starter_kit(got)
            parsed['repoStatus'] = 'pending_review'
            parsed['steps'] = []
            return parsed

        def work(progress):
            # Nhiệt độ thấp: đây là việc sinh code phải ĐÚNG, không phải viết sáng tạo.
            lab, audit_log = generate_with_self_correction(
                SYSTEM_PROMPT_REPO, user_message, audit_repo, build,
                temperature=0.15, model=model_for('repo'), report=progress,
            )

            if not ((lab.get('repo') or {}).get('files')):
                raise RuntimeError(
                    "Lõi không trả về file nào trong repo. Thử lại, hoặc đổi model "
                    "qua OPENAI_MODEL_REPO trong .env."
                )

            normalize_lab(lab)
            usage = summarize_usage(audit_log)
            lab['runId'] = (save_run(lab, 'repo', {'usage': usage}) or {}).get('runId')
            return {
                "lab": lab,
                "auditLog": audit_log,
                "usage": usage,
                "extraction_meta": {
                    "source_kind": source_kind,
                    "slide_pages_total": pages_total,
                    "slide_pages_used": pages_used,
                    "repo_files_found": len(file_tree),
                    "repo_core_files_used": core_used,
                },
            }

        # Trả jobId ngay, việc thật chạy ở luồng nền — xem vlearn/jobs.py.
        job_id = create_job('generate_repo')
        run_in_background(job_id, work)
        self.send_json_response({"success": True, "jobId": job_id}, status=202)

    # --- Giai đoạn 2 -------------------------------------------------------
    def handle_generate_tutorial(self, data):
        lab = data.get('lab') or {}
        files = ((lab.get('repo') or {}).get('files')) or []
        starter_kit = lab.get('starterKit') or derive_starter_kit(files)

        if not files:
            self.send_json_response({
                "success": False,
                "error": "Chưa có repo nào để sinh tutorial.",
            }, status=400)
            return

        # Repo test đỏ thì CẢNH BÁO chứ không chặn — Lab Coach là người quyết định.
        # Có những lúc họ biết rõ vì sao test đỏ (một ca biên chưa cần thiết, hay họ
        # định sửa tay sau) và vẫn muốn xem tutorial trước. Việc của hệ thống là nói
        # rõ hậu quả và bắt xác nhận, chứ không phải cấm.
        # Tên `test_report` chứ không phải `report`: bên trong work() có một tham số
        # tên `report` là HÀM báo tiến độ. Trùng tên là che mất nhau, và đó đúng là
        # lỗi đã xảy ra ('function' object has no attribute 'get').
        test_report = lab.get('testReport') or {}
        tests_green = (test_report.get('ran') and not test_report.get('timedOut')
                       and test_report.get('returncode') == 0
                       and test_report.get('passed', 0) > 0)

        if not tests_green and not data.get('allowFailingTests'):
            self.send_json_response({
                "success": False,
                "needsConfirmation": True,
                "testSummary": {
                    "ran": bool(test_report.get('ran')),
                    "passed": test_report.get('passed', 0),
                    "total": test_report.get('total', 0),
                    "reason": test_report.get('reason', ''),
                },
                "error": (
                    f"Repo mới pass {test_report.get('passed', 0)}/"
                    f"{test_report.get('total', 0)} test."
                    if test_report.get('ran') else
                    f"Repo chưa được chạy test: {test_report.get('reason', 'chưa rõ')}"
                ),
                "hint": "Gửi lại kèm allowFailingTests=true nếu vẫn muốn sinh tutorial.",
            }, status=409)
            return

        def work(progress):
            steps, audit_log = build_tutorial(lab, model_for('tutorial'), report=progress)

            if not steps:
                raise RuntimeError("Lõi không trả về bước nào cho tutorial.")

            lab['steps'] = steps
            lab['starterKit'] = starter_kit
            lab['repoStatus'] = 'approved'
            lab['status'] = 'tutorial_review'

            # Ghi dấu vĩnh viễn: bài này được sinh khi repo còn test đỏ. Coach có
            # thể quên, nhưng lịch sử thì không.
            if not tests_green:
                lab['generatedFromFailingTests'] = {
                    'passed': test_report.get('passed', 0),
                    'total': test_report.get('total', 0),
                    'ran': bool(test_report.get('ran')),
                }
            else:
                lab.pop('generatedFromFailingTests', None)

            normalize_lab(lab)

            # Chấm lần cuối: bố cục, toàn vẹn, mật độ giải thích.
            problems = audit_tutorial(lab)
            if problems:
                lab['selfCorrectionFailed'] = problems
                audit_log[0]['violations'] = problems
                audit_log[0]['passed'] = False

            usage = summarize_usage(audit_log)
            lab['runId'] = (save_run(lab, 'tutorial', {'usage': usage}) or {}).get('runId')
            return {
                "lab": lab,
                "repairedBlocks": [],
                "auditLog": audit_log,
                "usage": usage,
            }

        job_id = create_job('generate_tutorial')
        run_in_background(job_id, work)
        self.send_json_response({"success": True, "jobId": job_id}, status=202)

    # --- Đóng gói / mở gói -------------------------------------------------
    def handle_pack_repo(self, data):
        files = data.get('files') or []
        root = data.get('root_name') or 'repo'
        only = data.get('only_paths')

        if only is not None:
            allow = set(only)
            files = [f for f in files if f.get('path') in allow]

        if not files:
            self.send_json_response({"success": False, "error": "Không có file nào để đóng gói."}, status=400)
            return

        try:
            self.send_json_response({
                "success": True,
                "filename": f"{root}.zip",
                "zip_base64": files_to_zip_base64(files, root),
                "file_count": len(files),
            })
        except Exception as e:
            self.send_json_response({"success": False, "error": f"Đóng gói thất bại: {e}"}, status=500)

    def handle_unpack_repo(self, data):
        zip_b64 = data.get('zip_base64')
        if not zip_b64:
            self.send_json_response({"success": False, "error": "Thiếu file .zip."}, status=400)
            return

        try:
            files = zip_base64_to_files(zip_b64)
        except Exception as e:
            self.send_json_response({
                "success": False,
                "error": f"Không mở được file .zip: {e}",
                "hint": "Kiểm tra đúng định dạng .zip thật (không phải rar/7z đổi đuôi).",
            }, status=400)
            return

        if not files:
            self.send_json_response({
                "success": False,
                "error": "File .zip không chứa file text nào đọc được.",
            }, status=422)
            return

        self.send_json_response({
            "success": True,
            "files": files,
            "starter_kit": derive_starter_kit(files),
        })

    def handle_verify_lab(self, data):
        """Kiểm lại toàn bộ — kể cả CHẠY LẠI TEST THẬT sau khi Coach sửa repo."""
        lab = data.get('lab') or {}
        files = ((lab.get('repo') or {}).get('files')) or []
        normalize_lab(lab)

        repo_problems = audit_repo(lab) if data.get('run_tests') and files else []

        self.send_json_response({
            "success": True,
            "lab": lab,
            "problems": lab.get('integrityProblems') or [],
            "explanationProblems": lab.get('explanationProblems') or [],
            "repoProblems": repo_problems,
            "testReport": lab.get('testReport') or {},
            "warnings": lab.get('qualityWarnings') or [],
            "logicLines": count_logic_lines(files, lab.get('starterKit') or []),
        })

    def send_json_response(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
