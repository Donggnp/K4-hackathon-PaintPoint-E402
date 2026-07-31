// Điểm khởi động ứng dụng — nạp sau cùng, khi mọi module đã sẵn sàng.

// ---------------------------------------------------------------------------
// Khởi động
// ---------------------------------------------------------------------------
async function checkServerStatus() {
  try {
    const res = await fetch('/api/status');
    const status = await res.json();
    if (!status.has_pypdf) {
      console.warn('Thiếu pypdf — chức năng đọc Slide PDF sẽ lỗi.');
    }
  } catch (err) {
    console.warn('Không kết nối được backend:', err);
  }
}

state.projects.forEach(p => { checkIntegrity(p); });
checkServerStatus();
reloadRuns();
renderApp();
