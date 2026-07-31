// Trang cẩm nang — học viên đọc trên màn hình rồi tự gõ code trong IDE của mình.

// ---------------------------------------------------------------------------
// TRANG CẨM NANG — học viên đọc, tự gõ code trong IDE của mình
// ---------------------------------------------------------------------------
window.openCodelabWorkspace = function (id) {
  const p = findProject(id);
  if (!p || !(p.steps || []).length) return;
  state.activeCodelabId = id;
  state.activeStep = 0;
  startWorkspaceTimer(p.duration);
  renderApp();
};

window.closeWorkspace = function () {
  stopWorkspaceTimer();
  state.activeCodelabId = null;
  renderApp();
};

window.goToStep = function (stepNum) {
  state.activeStep = stepNum;
  renderApp();
  const main = document.querySelector('.ws-main');
  if (main) main.scrollTop = 0;
};

function renderWorkspacePage() {
  const lab = findProject(state.activeCodelabId);
  if (!lab) return '';

  const steps = lab.steps || [];
  const current = steps.find(s => s.num === state.activeStep) || steps[0];
  const total = steps.length;
  const isDraft = lab.status !== 'published';
  const idx = steps.indexOf(current);

  return `
    <div class="ws-page">
      ${isDraft ? `<div class="ws-draft-banner">👁️ BẢN XEM TRƯỚC — bài này <strong>chưa được phát hành</strong>. Học viên chưa nhìn thấy cho tới khi Lab Coach duyệt.</div>` : ''}
      <div class="ws-topbar">
        <button class="ws-back-btn" onclick="closeWorkspace()" title="Quay lại">←</button>
        <div class="ws-title">${escapeHtml(lab.title)}</div>
        <div class="ws-topbar-right">
          <span class="ws-timer-pill">🕐 Còn <span id="ws-timer">${formatTimer(state.timerSecondsLeft)}</span></span>
          <button class="theme-toggle-btn" onclick="toggleTheme()" title="Đổi giao diện">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
          </button>
        </div>
      </div>

      <div class="ws-body">
        <aside class="ws-sidebar">
          <div class="ws-step-list">
            ${steps.map(s => `
              <div class="ws-step-item ${s.num === state.activeStep ? 'current' : (s.num < state.activeStep ? 'done' : 'upcoming')}"
                   onclick="goToStep(${s.num})">
                <span class="ws-step-icon">${s.num < state.activeStep ? '✓' : s.num}</span>
                <span class="ws-step-label">${escapeHtml(s.title)}</span>
              </div>`).join('')}
          </div>
        </aside>

        <main class="ws-main">
          ${renderStepContent(lab, current)}
        </main>
      </div>

      <div class="ws-bottombar">
        <button class="btn-secondary" style="width:auto;"
                onclick="${idx > 0 ? `goToStep(${steps[idx - 1].num})` : 'closeWorkspace()'}">← Quay lại</button>
        <span class="ws-step-counter">${idx + 1} / ${total}</span>
        ${idx < total - 1
          ? `<button class="btn-primary" style="width:auto;" onclick="goToStep(${steps[idx + 1].num})">Tiếp →</button>`
          : `<button class="btn-primary" style="width:auto;" onclick="closeWorkspace()">🎉 Hoàn thành</button>`}
      </div>
    </div>
  `;
}

function renderStepContent(lab, step) {
  if (!step) return '';

  const isStepZero = step.num === 0;
  const kitCount = (lab.starterKit || []).length;

  return `
    <h2 class="ws-step-heading">${escapeHtml(step.title)}</h2>
    ${step.estimatedMinutes ? `<div class="ws-step-time">⏱️ Ước tính ~${step.estimatedMinutes} phút</div>` : ''}

    ${isStepZero ? `
      <div class="ws-download-card">
        <div>
          <div class="ws-download-title">Bộ khung khởi động — <code>${escapeHtml(lab.repoName || 'repo')}-starter.zip</code></div>
          <div class="ws-download-sub">${kitCount} file: cấu trúc thư mục, file cấu hình và
            <strong>toàn bộ ${((lab.summary || {}).testPlan || {}).total || ''} test đã viết sẵn</strong>.
            Không có file logic — đó là phần bạn sẽ tự viết.</div>
        </div>
        <button class="btn-primary" style="width:auto;" onclick="downloadStarterKit('${lab.id}')">
          ⬇️ Tải bộ khung khởi động (.zip)
        </button>
      </div>` : ''}

    ${(step.blocks || []).map((b, i) => renderBlock(lab, step, b, i)).join('')}
  `;
}

function renderBlock(lab, step, block, idx) {
  const type = block.type;

  if (type === 'text') {
    return `<div class="ws-text-block">${block.content || ''}</div>`;
  }

  if (type === 'code') {
    const lang = block.lang === 'bash' ? 'bash' : (block.lang || 'python');
    const label = block.filename || (lang === 'bash' ? 'terminal' : lang);
    const codeId = `code-${step.num}-${idx}`;
    const lines = (block.content || '').split('\n').length;
    return `
      <div class="ws-code-block">
        <div class="ws-code-head">
          <span class="ws-code-lang ${lang}">${escapeHtml(label)}</span>
          <span class="ws-code-meta">${block.filename ? `${lines} dòng` : ''}</span>
          <button class="ws-copy-btn" onclick="copyCode('${codeId}', this)">Copy</button>
        </div>
        <pre class="ws-code-body" id="${codeId}">${escapeHtml(block.content || '')}</pre>
      </div>`;
  }

  if (type === 'tree') {
    return `<div class="ws-tree-block">${(block.items || []).map(p => `<div class="ws-tree-item">${escapeHtml(p)}</div>`).join('')}</div>`;
  }

  if (type === 'callout') {
    const variant = ['info', 'warn', 'success'].includes(block.variant) ? block.variant : 'info';
    const icon = variant === 'warn' ? '⚠️' : (variant === 'success' ? '✅' : '💡');
    return `<div class="ws-callout ${variant}"><span class="ws-callout-icon">${icon}</span><div>${block.content || ''}</div></div>`;
  }

  if (type === 'checklist') {
    return `
      <div class="ws-checklist">
        <div class="ws-checklist-title">✓ Tự kiểm · Hoàn thành khi</div>
        ${(block.items || []).map((item, i) => {
          const key = `${lab.id}::${step.num}::${idx}::${i}`;
          return `
            <label class="ws-checklist-item">
              <input type="checkbox" ${state.checklist[key] ? 'checked' : ''} onchange="toggleCheck('${key}')">
              <span>${escapeHtml(item)}</span>
            </label>`;
        }).join('')}
      </div>`;
  }

  if (type === 'quiz') {
    const quizId = `quiz-${step.num}-${idx}`;
    return `
      <div class="ws-quiz-box">
        <h4>❓ Câu hỏi củng cố</h4>
        <p class="ws-quiz-question">${escapeHtml(block.question || '')}</p>
        <div class="ws-quiz-options">
          ${(block.options || []).map((opt, i) => `
            <button class="ws-quiz-opt"
                    onclick="handleQuizAnswer('${quizId}', ${i}, ${block.correct}, '${encodeURIComponent(block.explanation || '')}')">
              ${String.fromCharCode(65 + i)}. ${escapeHtml(opt)}
            </button>`).join('')}
        </div>
        <div id="${quizId}-result"></div>
      </div>`;
  }

  return '';
}

window.copyCode = function (codeId, btn) {
  const el = document.getElementById(codeId);
  if (!el) return;
  navigator.clipboard.writeText(el.textContent).then(() => {
    const old = btn.textContent;
    btn.textContent = '✓ Đã copy';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = old; btn.classList.remove('copied'); }, 1500);
  }).catch(() => { btn.textContent = 'Copy lỗi'; });
};

// Ô checkbox đã tự đổi trạng thái trên giao diện, chỉ cần ghi lại vào state.
window.toggleCheck = function (key) {
  state.checklist[key] = !state.checklist[key];
};

window.handleQuizAnswer = function (quizId, selectedIdx, correctIdx, explanationEncoded) {
  const box = document.getElementById(`${quizId}-result`);
  if (!box) return;
  const explanation = decodeURIComponent(explanationEncoded);

  box.innerHTML = selectedIdx === correctIdx
    ? `<div class="quiz-right"><strong>🎉 Chính xác!</strong><br>${escapeHtml(explanation)}</div>`
    : `<div class="quiz-wrong"><strong>❌ Chưa đúng.</strong><br>Hãy đọc lại phần giải thích phía trên rồi thử lại.</div>`;
};
