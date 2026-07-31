// Đồng hồ đếm ngược, chỉ dùng trên trang cẩm nang của học viên.

// ---------------------------------------------------------------------------
// Đồng hồ đếm ngược (chỉ trên trang cẩm nang)
// ---------------------------------------------------------------------------
function stopWorkspaceTimer() {
  if (state.timerInterval) clearInterval(state.timerInterval);
  state.timerInterval = null;
}

function startWorkspaceTimer(durationStr) {
  stopWorkspaceTimer();
  state.timerSecondsLeft = parseDurationMinutes(durationStr) * 60;
  state.timerInterval = setInterval(() => {
    state.timerSecondsLeft = Math.max(0, state.timerSecondsLeft - 1);
    const el = document.getElementById('ws-timer');
    if (el) el.textContent = formatTimer(state.timerSecondsLeft);
    if (state.timerSecondsLeft <= 0) stopWorkspaceTimer();
  }, 1000);
}
