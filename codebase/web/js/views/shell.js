// Khung điều hướng: quyết định đang hiển thị trang nào.

// ---------------------------------------------------------------------------
// Bộ khung điều hướng
// ---------------------------------------------------------------------------
function renderApp() {
  const root = document.getElementById('app');

  if (state.explorerProjectId) { root.innerHTML = renderExplorerPage(); wireExplorer(); return; }
  if (state.activeCodelabId) { root.innerHTML = renderWorkspacePage(); return; }

  root.innerHTML = `
    <div class="role-bar">
      <div class="role-info"><span>VLEARN • MINI CODELAB GENERATOR</span></div>
      <div class="role-switcher">
        <button class="role-btn ${state.currentRole === 'student' ? 'active' : ''}" onclick="switchRole('student')">👨‍🎓 Học viên</button>
        <button class="role-btn ${state.currentRole === 'coach' ? 'active' : ''}" onclick="switchRole('coach')">👨‍🏫 Lab Coach Studio</button>
      </div>
    </div>

    <header class="vlearn-header">
      <div class="header-left">
        <a href="#" class="brand-logo" onclick="event.preventDefault()">
          <svg class="brand-icon" viewBox="0 0 32 32" fill="none">
            <path d="M6 8L16 26L26 8" stroke="#C8102E" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 8L16 16L20 8" stroke="#0C2340" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>VLearn</span>
        </a>
      </div>
      <div class="header-right">
        <button class="theme-toggle-btn" onclick="toggleTheme()" title="Đổi giao diện sáng/tối">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
        </button>
      </div>
    </header>

    <main class="page-container">
      ${state.currentRole === 'student' ? renderStudentDashboard() : renderCoachStudio()}
    </main>

    <footer class="vlearn-footer">
      <p>© 2026 VLearn — Nền tảng học tập VinUni AI Thực Chiến</p>
    </footer>
  `;
}

window.switchRole = function (role) {
  state.currentRole = role;
  renderApp();
  if (role === 'coach') reloadRuns();      // lịch sử đọc từ đĩa, luôn lấy bản mới nhất
};

window.toggleTheme = function () {
  state.theme = state.theme === 'light' ? 'dark' : 'light';
  document.body.classList.toggle('dark-mode', state.theme === 'dark');
};
