// File Explorer: cây thư mục bên trái, nội dung file sửa được bên phải.

// ---------------------------------------------------------------------------
// FILE EXPLORER — cây thư mục bên trái, nội dung file bên phải
// ---------------------------------------------------------------------------
function buildFileTree(files) {
  const root = { name: '', path: '', dirs: {}, files: [] };

  files.forEach(f => {
    const parts = f.path.split('/');
    let node = root;
    for (let i = 0; i < parts.length - 1; i++) {
      const dirPath = parts.slice(0, i + 1).join('/');
      if (!node.dirs[parts[i]]) {
        node.dirs[parts[i]] = { name: parts[i], path: dirPath, dirs: {}, files: [] };
      }
      node = node.dirs[parts[i]];
    }
    node.files.push({ name: parts[parts.length - 1], path: f.path });
  });

  return root;
}

function renderTreeNode(project, node, depth) {
  const pad = 10 + depth * 14;
  let html = '';

  Object.keys(node.dirs).sort().forEach(name => {
    const dir = node.dirs[name];
    const collapsed = !!state.collapsedDirs[dir.path];
    html += `
      <div class="fx-node fx-dir" style="padding-left:${pad}px" onclick="toggleDir('${escapeHtml(dir.path)}')">
        <span class="fx-caret">${collapsed ? '▸' : '▾'}</span>
        <span class="fx-icon">📁</span><span class="fx-name">${escapeHtml(name)}</span>
      </div>`;
    if (!collapsed) html += renderTreeNode(project, dir, depth + 1);
  });

  node.files.sort((a, b) => a.name.localeCompare(b.name)).forEach(f => {
    const active = state.explorerPath === f.path;
    const kit = isStarterKitPath(project, f.path);
    html += `
      <div class="fx-node fx-file ${active ? 'active' : ''}" style="padding-left:${pad + 14}px"
           onclick="openFile('${escapeHtml(f.path)}')" title="${escapeHtml(f.path)}">
        <span class="fx-icon">${kit ? '🧰' : '📄'}</span><span class="fx-name">${escapeHtml(f.name)}</span>
      </div>`;
  });

  return html;
}

function renderExplorerPage() {
  const p = findProject(state.explorerProjectId);
  if (!p) return '';

  const files = repoFiles(p);
  const current = files.find(f => f.path === state.explorerPath) || files[0] || null;
  if (current) state.explorerPath = current.path;

  const lineCount = current ? (current.content || '').split('\n').length : 0;
  const gutter = Array.from({ length: lineCount }, (_, i) => i + 1).join('\n');
  const kit = current ? isStarterKitPath(p, current.path) : false;
  const problems = p.integrityProblems || [];

  return `
    <div class="fx-page">
      <div class="fx-topbar">
        <button class="ws-back-btn" onclick="closeExplorer()" title="Quay lại">←</button>
        <div class="fx-title">
          <strong>${escapeHtml(p.repoName || 'repo')}</strong>
          <span class="fx-subtitle">${escapeHtml(p.title)}</span>
        </div>
        <div class="fx-actions">
          <span class="fx-stat">${files.length} file · ${countLogicLines(p)} dòng logic</span>
          <button class="btn-secondary" onclick="downloadRepo('${p.id}')">⬇️ Tải repo (.zip)</button>
          <label class="btn-secondary fx-upload">
            ⬆️ Upload repo đã sửa
            <input type="file" accept=".zip" onchange="uploadRepo('${p.id}', this)" hidden>
          </label>
          <button class="theme-toggle-btn" onclick="toggleTheme()" title="Đổi giao diện">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
          </button>
        </div>
      </div>

      ${problems.length ? `
        <div class="fx-alert">⚠️ ${problems.length} chỗ tutorial đang lệch với repo.
          <button class="link-btn" onclick="syncTutorial('${p.id}')">Đồng bộ tutorial theo repo</button>
        </div>` : ''}

      <div class="fx-body">
        <aside class="fx-sidebar">
          <div class="fx-sidebar-head">CẤU TRÚC THƯ MỤC</div>
          ${renderTreeNode(p, buildFileTree(files), 0)}
          <div class="fx-legend">🧰 file có sẵn ở Bước 0 &nbsp;·&nbsp; 📄 file học viên tự viết</div>
        </aside>

        <main class="fx-main">
          ${current ? `
            <div class="fx-filebar">
              <span class="fx-filepath">${escapeHtml(current.path)}</span>
              <span class="fx-filetag ${kit ? 'kit' : 'logic'}">${kit ? 'bộ khung khởi động' : 'file logic — học viên tự gõ'}</span>
              <span class="fx-filelines">${lineCount} dòng</span>
              <span class="fx-saved" id="fx-saved"></span>
            </div>
            <div class="fx-editor">
              <pre class="fx-gutter" id="fx-gutter">${gutter}</pre>
              <textarea class="fx-code" id="fx-code" spellcheck="false"
                        oninput="onFileEdit('${p.id}')">${escapeHtml(current.content || '')}</textarea>
            </div>
          ` : `<div class="empty-state"><p>Repo chưa có file nào.</p></div>`}
        </main>
      </div>
    </div>
  `;
}

// Đồng bộ cuộn giữa cột số dòng và vùng soạn thảo.
function wireExplorer() {
  const code = document.getElementById('fx-code');
  const gutter = document.getElementById('fx-gutter');
  if (code && gutter) {
    code.addEventListener('scroll', () => { gutter.scrollTop = code.scrollTop; });
  }
}

window.toggleDir = function (path) {
  state.collapsedDirs[path] = !state.collapsedDirs[path];
  renderApp();
};

window.openFile = function (path) {
  state.explorerPath = path;
  renderApp();
};

window.openExplorer = function (projectId, path) {
  state.explorerProjectId = projectId;
  state.explorerPath = path || null;
  renderApp();
};

window.closeExplorer = function () {
  state.explorerProjectId = null;
  state.explorerPath = null;
  renderApp();
};

// Sửa file: cập nhật repo, đồng bộ ngay vào tutorial, rồi kiểm tra tính toàn vẹn.
window.onFileEdit = function (projectId) {
  const p = findProject(projectId);
  const textarea = document.getElementById('fx-code');
  if (!p || !textarea) return;

  const file = repoFiles(p).find(f => f.path === state.explorerPath);
  if (!file) return;

  file.content = textarea.value;

  const gutter = document.getElementById('fx-gutter');
  const lines = textarea.value.split('\n').length;
  if (gutter) gutter.textContent = Array.from({ length: lines }, (_, i) => i + 1).join('\n');

  if ((p.steps || []).length) syncTutorialToRepo(p);
  recomputeDuration(p);

  const saved = document.getElementById('fx-saved');
  if (saved) {
    saved.textContent = '● đã lưu vào bản nháp';
    clearTimeout(window.__savedTimer);
    window.__savedTimer = setTimeout(() => { saved.textContent = ''; }, 1500);
  }
};
