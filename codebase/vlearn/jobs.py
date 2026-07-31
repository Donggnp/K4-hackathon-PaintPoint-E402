"""Chạy việc sinh bài ở luồng nền, và báo tiến độ cho giao diện.

Vì sao cần? Một lượt sinh mất từ 30 giây tới vài phút (gọi model + chạy test
Docker, có thể lặp vài vòng). Nếu giữ kết nối HTTP suốt thời gian đó thì:

  - trình duyệt chỉ thấy một request treo, không biết đang làm gì, dễ tưởng hỏng;
  - proxy hoặc trình duyệt có thể tự cắt kết nối giữa chừng;
  - người dùng bấm F5 là mất trắng công sinh đang chạy.

Cách làm: POST trả về ngay một `jobId`, việc thật chạy ở luồng nền, giao diện
hỏi tiến độ mỗi 2 giây. Người dùng thấy "Vòng 2/3 — đang chạy test trong
Docker (1m 12s)" thay vì một vòng xoay im lặng.

Lưu trong bộ nhớ tiến trình, không có database — đúng phạm vi hackathon. Job cũ
tự bị dọn sau JOB_TTL_SECONDS để không rò rỉ bộ nhớ.
"""

import threading
import time
import traceback
import uuid

JOB_TTL_SECONDS = 3600
_jobs = {}
_lock = threading.Lock()


def _prune():
    """Dọn job đã xong quá lâu. Gọi mỗi lần tạo job mới là đủ."""
    now = time.time()
    for job_id in [k for k, v in _jobs.items()
                   if v['finishedAt'] and now - v['finishedAt'] > JOB_TTL_SECONDS]:
        _jobs.pop(job_id, None)


def create_job(kind):
    job_id = uuid.uuid4().hex[:12]
    with _lock:
        _prune()
        _jobs[job_id] = {
            'id': job_id,
            'kind': kind,
            'status': 'running',
            'startedAt': time.time(),
            'finishedAt': None,
            'progress': {'phase': 'Đang chuẩn bị…', 'round': 0, 'totalRounds': 0},
            'result': None,
            'error': None,
        }
    return job_id


def set_progress(job_id, phase, round_no=None, total_rounds=None, detail=None):
    """Cập nhật tiến độ. An toàn khi job đã bị dọn (bỏ qua)."""
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        p = job['progress']
        p['phase'] = phase
        if round_no is not None:
            p['round'] = round_no
        if total_rounds is not None:
            p['totalRounds'] = total_rounds
        if detail is not None:
            p['detail'] = detail
        p['elapsed'] = round(time.time() - job['startedAt'], 1)


def run_in_background(job_id, fn):
    """Chạy `fn(report)` ở luồng nền; `report` là hàm cập nhật tiến độ."""
    def report(phase, **kw):
        set_progress(job_id, phase, **kw)

    def worker():
        try:
            result = fn(report)
            with _lock:
                job = _jobs.get(job_id)
                if job:
                    job.update(status='done', result=result, finishedAt=time.time())
                    job['progress']['phase'] = 'Hoàn tất'
        except Exception as e:
            # Nuốt exception ở đây là CỐ Ý: luồng nền chết lặng lẽ thì giao diện
            # sẽ chờ mãi. Ghi lại lỗi để trả về cho người dùng đọc được.
            traceback.print_exc()
            with _lock:
                job = _jobs.get(job_id)
                if job:
                    job.update(status='error', error=str(e), finishedAt=time.time())

    threading.Thread(target=worker, daemon=True).start()


def get_job(job_id):
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return None
        snapshot = dict(job)
        snapshot['progress'] = dict(job['progress'])
        snapshot['elapsed'] = round(
            (job['finishedAt'] or time.time()) - job['startedAt'], 1)
        return snapshot
