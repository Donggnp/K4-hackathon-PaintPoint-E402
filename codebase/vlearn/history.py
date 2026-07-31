"""Lưu lịch sử mọi lượt sinh ra đĩa, để Lab Coach mở lại bất cứ lúc nào.

Vì sao cần? Mọi thứ trước đây chỉ nằm trong state của trình duyệt: reload trang là
mất trắng công sinh, và không có cách nào đối chiếu bài hôm nay với bài tuần trước.

Mỗi lượt được lưu thành một thư mục ĐỌC ĐƯỢC BẰNG MẮT, không phải một cục JSON:

    runs/2026-07-31T13-20-05__mini-react-agent/
        manifest.json     tóm tắt: thời gian, model, token, test pass mấy/mấy
        lab.json          toàn bộ dữ liệu để nạp lại vào Studio
        repo/             cây thư mục THẬT — mở bằng IDE, chạy pytest được ngay
        tutorial.md       tutorial dạng Markdown, đọc thẳng không cần app
        test-output.txt   log pytest nguyên văn của lượt đó

Nhờ vậy ngay cả khi app hỏng, thư mục này vẫn còn nguyên giá trị.
"""

import json
import os
import re
import shutil
from datetime import datetime

from .config import RUNS_DIR

_SAFE = re.compile(r'[^a-zA-Z0-9._-]+')


def _slug(text, fallback='lab'):
    s = _SAFE.sub('-', (text or '').strip()).strip('-').lower()
    return s[:60] or fallback


def _test_summary(lab):
    """Rút gọn trạng thái test thành thứ đọc lướt là hiểu."""
    r = lab.get('testReport') or {}
    if not r.get('ran'):
        return {'state': 'not_run', 'label': 'chưa chạy test',
                'passed': 0, 'total': 0, 'sandbox': r.get('sandbox')}
    if r.get('timedOut'):
        return {'state': 'timeout', 'label': 'test bị treo',
                'passed': 0, 'total': 0, 'sandbox': r.get('sandbox')}
    green = r.get('returncode') == 0 and r.get('passed', 0) > 0
    return {
        'state': 'passed' if green else 'failed',
        'label': (f"{r.get('passed', 0)}/{r.get('total', 0)} test pass"
                  if green else f"ĐỎ — {r.get('passed', 0)}/{r.get('total', 0)}"),
        'passed': r.get('passed', 0),
        'total': r.get('total', 0),
        'sandbox': r.get('sandbox'),
    }


def _tutorial_markdown(lab):
    """Xuất tutorial ra Markdown để đọc được mà không cần mở app."""
    out = [f"# {lab.get('title', '')}", '']
    if lab.get('description'):
        out += [lab['description'], '']
    out += [
        f"- **Repo:** `{lab.get('repoName', '')}`",
        f"- **Thời lượng:** {lab.get('duration', '')}",
        f"- **Nguồn lý thuyết:** {lab.get('morningSlideRef', '')}",
        '',
    ]

    for step in lab.get('steps') or []:
        out += ['---', '', f"## {step.get('title', '')}", '']
        for block in step.get('blocks') or []:
            kind = block.get('type')
            if kind in ('text', 'callout'):
                text = re.sub(r'<br\s*/?>', '\n', block.get('content') or '')
                text = re.sub(r'</(p|li|ul|ol)>', '\n', text)
                text = re.sub(r'<li>', '- ', text)
                text = re.sub(r'<[^>]+>', '', text).strip()
                if kind == 'callout':
                    text = '> ' + text.replace('\n', '\n> ')
                out += [text, '']
            elif kind == 'code':
                lang = block.get('lang') or 'python'
                if block.get('filename'):
                    out.append(f"**`{block['filename']}`**")
                out += [f"```{lang}", (block.get('content') or '').rstrip(), '```', '']
            elif kind == 'tree':
                out += ['```', *(block.get('items') or []), '```', '']
            elif kind == 'checklist':
                out += [f"- [ ] {i}" for i in (block.get('items') or [])] + ['']
            elif kind == 'quiz':
                out += [f"**❓ {block.get('question', '')}**", '']
                for i, opt in enumerate(block.get('options') or []):
                    out.append(f"{chr(65 + i)}. {opt}")
                out += ['', f"<details><summary>Đáp án</summary>\n\n"
                            f"{chr(65 + (block.get('correct') or 0))} — "
                            f"{block.get('explanation', '')}\n\n</details>", '']
    return '\n'.join(out)


def save_run(lab, stage, extra=None):
    """Lưu một lượt sinh. Trả về manifest, hoặc None nếu không lưu được.

    Không bao giờ ném exception ra ngoài: hỏng việc ghi log thì cũng không được
    làm sập luồng sinh bài mà Coach đang chờ.
    """
    try:
        os.makedirs(RUNS_DIR, exist_ok=True)
        stamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        run_id = f"{stamp}__{_slug(lab.get('repoName'))}"
        root = os.path.join(RUNS_DIR, run_id)

        # Cùng một giây có thể sinh 2 lượt (hiếm) — thêm hậu tố cho khỏi đè nhau.
        suffix = 1
        while os.path.exists(root):
            suffix += 1
            run_id = f"{stamp}-{suffix}__{_slug(lab.get('repoName'))}"
            root = os.path.join(RUNS_DIR, run_id)
        os.makedirs(root)

        # Cây repo thật — mở bằng IDE và chạy pytest được ngay.
        repo_root = os.path.abspath(os.path.join(root, 'repo'))
        for f in (lab.get('repo') or {}).get('files', []):
            path = (f.get('path') or '').lstrip('/')
            full = os.path.normpath(os.path.join(repo_root, path))
            if not full.startswith(repo_root + os.sep):
                continue                      # chặn đường dẫn thoát ra ngoài
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, 'w', encoding='utf-8') as fh:
                fh.write(f.get('content') or '')

        with open(os.path.join(root, 'lab.json'), 'w', encoding='utf-8') as fh:
            json.dump(lab, fh, ensure_ascii=False, indent=2)

        if lab.get('steps'):
            with open(os.path.join(root, 'tutorial.md'), 'w', encoding='utf-8') as fh:
                fh.write(_tutorial_markdown(lab))

        report = lab.get('testReport') or {}
        if report.get('fullOutput') or report.get('output'):
            with open(os.path.join(root, 'test-output.txt'), 'w', encoding='utf-8') as fh:
                fh.write(f"$ {report.get('command', 'pytest -v')}\n\n"
                         f"{report.get('fullOutput') or report.get('output')}\n")

        usage = (extra or {}).get('usage') or {}
        manifest = {
            'runId': run_id,
            'stage': stage,                       # 'repo' | 'tutorial' | 'published'
            'savedAt': datetime.now().isoformat(timespec='seconds'),
            'title': lab.get('title', ''),
            'repoName': lab.get('repoName', ''),
            'status': lab.get('status', ''),
            'duration': lab.get('duration', ''),
            'fileCount': len((lab.get('repo') or {}).get('files', [])),
            'stepCount': len(lab.get('steps') or []),
            'tests': _test_summary(lab),
            'model': usage.get('model'),
            'rounds': usage.get('rounds'),
            'totalTokens': usage.get('totalTokens'),
            'qualityWarnings': lab.get('qualityWarnings') or [],
            'integrityProblems': len(lab.get('integrityProblems') or []),
            'generatedFromFailingTests': lab.get('generatedFromFailingTests'),
        }
        with open(os.path.join(root, 'manifest.json'), 'w', encoding='utf-8') as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=2)

        return manifest
    except Exception as e:
        print(f"[history] không lưu được lượt chạy: {e}", flush=True)
        return None


def list_runs(limit=100):
    """Danh sách lượt chạy, mới nhất trước."""
    if not os.path.isdir(RUNS_DIR):
        return []

    runs = []
    for name in sorted(os.listdir(RUNS_DIR), reverse=True)[:limit]:
        path = os.path.join(RUNS_DIR, name, 'manifest.json')
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding='utf-8') as fh:
                runs.append(json.load(fh))
        except Exception:
            continue
    return runs


def load_run(run_id):
    """Nạp lại toàn bộ lab của một lượt chạy cũ."""
    root = os.path.join(RUNS_DIR, os.path.basename(run_id))
    path = os.path.join(root, 'lab.json')
    if not os.path.isfile(path):
        return None
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def delete_run(run_id):
    root = os.path.join(RUNS_DIR, os.path.basename(run_id))
    if not os.path.isdir(root):
        return False
    shutil.rmtree(root, ignore_errors=True)
    return True
