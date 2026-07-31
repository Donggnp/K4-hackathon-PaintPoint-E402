// Vai LAB COACH — quản lý, tạo, soát và duyệt mini-project.

// ---------------------------------------------------------------------------
// LAB COACH — danh sách toàn bộ mini-project + tạo mới + hai cửa duyệt
// ---------------------------------------------------------------------------
function renderCoachStudio() {
  return `
    <div class="section-header">
      <div>
        <div class="breadcrumb-tag">LAB COACH STUDIO</div>
        <h1 class="page-title">Quản lý & tạo Mini Codelab</h1>
        <p class="page-subtitle">
          Nạp slide sáng + repo lab chiều. AI sinh repo trước — bạn duyệt repo rồi mới tới tutorial.
        </p>
      </div>
    </div>

    ${renderProjectRegistry()}
    ${renderRunHistory()}
    ${renderGenerateForm()}
    ${state.projects.filter(p => p.status === 'repo_review').map(renderRepoReview).join('')}
    ${state.projects.filter(p => p.status === 'tutorial_review').map(renderTutorialReview).join('')}
  `;
}

// Lịch sử mọi lượt sinh, đọc từ đĩa (codebase/runs/). Coach mở lại bất cứ lúc nào.
//
// Vì sao cần? Trước đây mọi thứ chỉ nằm trong bộ nhớ trình duyệt: reload trang là
// mất trắng, và không đối chiếu được bài hôm nay với bài tuần trước.
const TEST_STATE_BADGE = {
  passed: { cls: 'st-published', icon: '✅' },
  failed: { cls: 'st-broken', icon: '❌' },
  timeout: { cls: 'st-broken', icon: '⏱️' },
  not_run: { cls: 'st-repo', icon: '⚪' },
};

function renderRunHistory() {
  const runs = state.runs || [];

  return `
    <div class="coach-studio-card">
      <h3 class="coach-section-title" style="margin-top:0;">
        📚 Lịch sử các lượt đã chạy (${runs.length})
        <button class="link-btn" style="margin-left:10px;" onclick="reloadRuns()">↻ Tải lại</button>
      </h3>
      <p class="coach-review-hint" style="margin-top:0;">
        Mỗi lượt được lưu ra đĩa tại <code>codebase/runs/</code>: repo dạng cây thư mục thật
        (mở IDE chạy <code>pytest</code> được ngay), tutorial dạng Markdown, và log test nguyên văn.
        Bấm <strong>Nạp lại</strong> để đưa một lượt cũ trở lại Studio.
      </p>

      ${runs.length === 0 ? `
        <p style="color:var(--text-muted);">Chưa có lượt nào. Sinh bài đầu tiên ở khung bên dưới.</p>
      ` : `
        <div class="registry-list">
          ${runs.map(r => {
            const t = r.tests || {};
            const badge = TEST_STATE_BADGE[t.state] || TEST_STATE_BADGE.not_run;
            return `
            <div class="registry-row">
              <div class="registry-main">
                <div class="registry-badges">
                  <span class="status-badge ${badge.cls}">${badge.icon} ${escapeHtml(t.label || '')}</span>
                  <span class="run-stage">${escapeHtml(r.stage || '')}</span>
                  ${(r.qualityWarnings || []).length
                    ? `<span class="status-badge st-broken">⚠️ ${r.qualityWarnings.length} cảnh báo</span>` : ''}
                </div>
                <strong class="registry-title">${escapeHtml(r.title || r.repoName || '')}</strong>
                <div class="registry-meta">
                  <code>${escapeHtml(r.runId || '')}</code><br>
                  ${escapeHtml(r.savedAt || '')} ·
                  ${r.fileCount || 0} file ·
                  ${r.stepCount ? `${r.stepCount} bước · ` : 'chưa có tutorial · '}
                  ${escapeHtml(r.model || '?')}${r.rounds ? ` · ${r.rounds} vòng` : ''}${
                    r.totalTokens ? ` · ${r.totalTokens.toLocaleString()} token` : ''}
                </div>
              </div>
              <div class="registry-actions">
                <button class="btn-secondary" onclick="restoreRun('${escapeHtml(r.runId)}')">↩️ Nạp lại</button>
                <button class="btn-danger" onclick="deleteRun('${escapeHtml(r.runId)}')">🗑️ Xoá</button>
              </div>
            </div>`;
          }).join('')}
        </div>
      `}
    </div>
  `;
}

function renderProjectRegistry() {
  if (!state.projects.length) {
    return `<div class="coach-studio-card">
      <h3 class="coach-section-title" style="margin-top:0;">Tất cả Mini-project</h3>
      <p style="color:var(--text-muted);">Chưa có mini-project nào. Tạo bài đầu tiên ở khung bên dưới.</p>
    </div>`;
  }

  return `
    <div class="coach-studio-card">
      <h3 class="coach-section-title" style="margin-top:0;">
        Tất cả Mini-project (${state.projects.length})
      </h3>
      <p class="coach-review-hint" style="margin-top:0;">
        Học viên chỉ nhìn thấy bài có trạng thái <strong>ĐÃ PHÁT HÀNH</strong>.
      </p>
      <div class="registry-list">
        ${state.projects.map(p => {
          const st = STATUS_LABEL[p.status] || STATUS_LABEL.repo_review;
          const problems = (p.integrityProblems || []).length;
          return `
          <div class="registry-row">
            <div class="registry-main">
              <div class="registry-badges">
                <span class="status-badge ${st.cls}">${st.text}</span>
                ${problems ? `<span class="status-badge st-broken">⚠️ ${problems} sai lệch</span>` : ''}
              </div>
              <strong class="registry-title">${escapeHtml(p.title)}</strong>
              <div class="registry-meta">
                repo <code>${escapeHtml(p.repoName || '—')}</code>
                · ${repoFiles(p).length} file
                · ${countLogicLines(p)} dòng logic
                · ${(p.steps || []).length ? `${(p.steps || []).length - 1} phase · ${escapeHtml(p.duration || '')}` : 'chưa có tutorial'}
              </div>
            </div>
            <div class="registry-actions">
              <button class="btn-secondary" onclick="openExplorer('${p.id}')">🗂️ Mở repo</button>
              ${(p.steps || []).length
                ? `<button class="btn-secondary" onclick="openCodelabWorkspace('${p.id}')">📖 Xem tutorial</button>`
                : ''}
              ${p.status === 'published'
                ? `<button class="btn-secondary" onclick="unpublishProject('${p.id}')">⏸️ Gỡ xuống</button>`
                : ''}
              <button class="btn-danger" onclick="deleteProject('${p.id}')">🗑️ Xoá</button>
            </div>
          </div>`;
        }).join('')}
      </div>
    </div>
  `;
}

function renderGenerateForm() {
  return `
    <div class="coach-studio-card">
      <h3 class="coach-section-title" style="margin-top:0;">Tạo Mini-project mới</h3>
      <form onsubmit="event.preventDefault(); handleGenerateRepo();">
        <div class="form-group">
          <label class="form-label">1. Slide lý thuyết buổi sáng (.pdf) — bắt buộc</label>
          <input type="file" id="coach-slide-pdf" class="form-control" accept="application/pdf">
          <small class="form-hint">Hệ thống đọc text theo từng trang để trích dẫn đúng số trang.</small>
        </div>

        <div class="form-group">
          <label class="form-label">2. Mô tả lab buổi chiều — bắt buộc, chọn 1 trong 2 cách</label>

          <div class="source-picker">
            <label class="source-option ${state.labSource === 'readme' ? 'active' : ''}">
              <input type="radio" name="lab-source" value="readme"
                     ${state.labSource === 'readme' ? 'checked' : ''}
                     onchange="setLabSource('readme')">
              <div>
                <strong>📄 README.md</strong>
                <span>Nhẹ, nhanh. Đủ dùng khi README nói rõ lab chiều làm gì.</span>
              </div>
            </label>
            <label class="source-option ${state.labSource === 'zip' ? 'active' : ''}">
              <input type="radio" name="lab-source" value="zip"
                     ${state.labSource === 'zip' ? 'checked' : ''}
                     onchange="setLabSource('zip')">
              <div>
                <strong>📦 Cả repo (.zip)</strong>
                <span>Nhiều ngữ cảnh nhất, nhưng file có thể rất nặng.</span>
              </div>
            </label>
          </div>

          ${state.labSource === 'readme' ? `
            <input type="file" id="coach-readme-file" class="form-control" accept=".md,.markdown,.txt"
                   style="margin-top:10px;">
            <small class="form-hint">Hoặc dán thẳng nội dung README vào ô dưới đây:</small>
            <textarea id="coach-readme-text" class="form-control" rows="6"
                      placeholder="# Tên lab buổi chiều&#10;&#10;## Mục tiêu&#10;...&#10;&#10;## Kiến trúc&#10;...&#10;&#10;## Công nghệ sử dụng&#10;..."></textarea>
          ` : `
            <input type="file" id="coach-repo-zip" class="form-control" accept=".zip" style="margin-top:10px;">
            <small class="form-hint">Chỉ đọc file tree + file cốt lõi (README, entry point, file dependency).
              Hệ thống tự lọc <code>node_modules</code>, <code>venv</code>, <code>.git</code>.</small>
          `}
        </div>

        <div class="form-group">
          <label class="form-label">3. Ràng buộc thêm cho AI (tuỳ chọn)</label>
          <textarea id="coach-prompt-rules" class="form-control" rows="3" placeholder="Ví dụ: bám sát phần ReAct loop trong slide, đừng dùng thư viện ngoài."></textarea>
        </div>

        <button type="submit" id="btn-generate-repo" class="btn-primary" style="font-size:15px; padding:12px 24px;">
          <span>✨ Bước 1 — Sinh repo mini-project</span>
        </button>
      </form>
      <div id="coach-generation-progress" style="display:none;"></div>
    </div>
  `;
}

function renderRepoReview(p) {
  const problems = p.integrityProblems || [];
  const warnings = p.qualityWarnings || [];
  const s = p.summary || {};

  return `
    <div class="coach-review-card">
      <div class="coach-review-head">
        <div>
          <span class="status-badge st-repo">📦 CHỜ DUYỆT REPO</span>
          <h2 class="coach-review-title">${escapeHtml(p.title)}</h2>
          <p class="coach-review-meta">
            ${repoFiles(p).length} file · ${countLogicLines(p)} dòng logic
            · ${(s.testPlan || {}).total || 0} test · repo <code>${escapeHtml(p.repoName || '')}</code>
          </p>
        </div>
        <div class="coach-review-actions">
          <button class="btn-secondary" onclick="openExplorer('${p.id}')">🗂️ Mở & sửa repo</button>
          <button class="btn-secondary" onclick="rerunTests('${p.id}')">🧪 Chạy lại test</button>
          <button class="${testsGreen(p) ? 'btn-primary' : 'btn-warning'}"
                  title="${testsGreen(p) ? 'Repo đã pass 100% test' : 'Repo chưa pass hết test — hệ thống sẽ hỏi lại trước khi sinh'}"
                  onclick="approveRepoAndGenerateTutorial('${p.id}')">
            ${testsGreen(p) ? '✅ Duyệt repo &amp; sinh tutorial' : '⚠️ Duyệt dù test chưa xanh &amp; sinh tutorial'}
          </button>
        </div>
      </div>

      ${renderTestPanel(p)}
      ${renderAuditPanel(p)}

      ${warnings.length ? `
        <div class="coach-quality-warn">
          <strong>⚠️ Hệ thống tự kiểm và thấy:</strong>
          <ul>${warnings.map(w => `<li>${escapeHtml(w)}</li>`).join('')}</ul>
        </div>` : ''}

      <p class="coach-review-hint">
        Đọc kỹ bản tóm tắt dưới đây, mở repo để soát từng file, chạy thử test trên máy bạn nếu cần.
        <strong>Chỉ khi bạn duyệt repo, AI mới bắt đầu viết tutorial</strong> — và tutorial sẽ được sinh
        từ đúng repo này, nên repo càng chuẩn thì tutorial càng chuẩn.
      </p>

      ${renderSummaryPanel(p)}
    </div>
  `;
}

// Token thật đã tiêu — để Coach tự tính chi phí bằng bảng giá của mình.
function renderUsageLine(p) {
  const u = p.usage;
  if (!u || !u.totalTokens) return '';
  return `<p class="usage-line">
    📊 <strong>${escapeHtml(u.model || '')}</strong> ·
    ${u.rounds} vòng ·
    vào ${u.promptTokens.toLocaleString()} token ·
    ra ${u.completionTokens.toLocaleString()} token ·
    tổng <strong>${u.totalTokens.toLocaleString()}</strong>
  </p>`;
}

// Lõi đã phải sửa mấy vòng, và còn vi phạm gì không — hiện thẳng cho Coach.
// Kết quả CHẠY THẬT pytest trên repo do lõi sinh ra.
// Repo chỉ được duyệt khi ĐÃ CHẠY THẬT và pass 100% test.
// Không có bằng chứng này thì việc duyệt chỉ là đoán.
function testsGreen(p) {
  const r = p.testReport;
  return !!(r && r.ran && !r.timedOut && r.returncode === 0 && r.passed > 0);
}

// Số test hỏng. Suy ra từ tổng khi báo cáo thiếu trường `failed`, để không bao
// giờ hiện ra thứ tự mâu thuẫn kiểu "KHÔNG PASS TEST — 27 pass, 0 fail".
function failedCount(r) {
  if (typeof r.failed === 'number' && r.failed > 0) return r.failed;
  const derived = (r.total || 0) - (r.passed || 0);
  return derived > 0 ? derived : '?';
}

// Kết quả CHẠY THẬT pytest trong sandbox Docker.
//
// Coach cần thấy BẰNG CHỨNG, không phải lời hứa: tên từng test, log terminal
// nguyên văn, và lệnh docker đã dùng. Đây là thứ họ nhìn trước khi bấm duyệt.
function renderTestPanel(p) {
  const r = p.testReport;

  // Chưa có báo cáo nào = chưa có bằng chứng nào. Phải nói rõ, vì im lặng ở đây
  // dễ khiến Coach tưởng mọi thứ ổn.
  if (!r) {
    return `<div class="coach-integrity-fail">
      <strong>🧪 CHƯA CHẠY ĐƯỢC TEST</strong>
      <p>Repo này chưa được chạy test lần nào, nên chưa có bằng chứng nào cho thấy
         học viên làm theo sẽ thấy test xanh.</p>
      <p>Bấm <strong>🧪 Chạy lại test</strong> để chạy trong sandbox Docker.</p>
    </div>`;
  }

  const sandboxBadge = {
    docker: '<span class="sandbox-badge ok">🐳 Docker sandbox</span>',
    'host-unsafe': '<span class="sandbox-badge warn">⚠️ Chạy trên máy thật</span>',
    unavailable: '<span class="sandbox-badge bad">🚫 Không có sandbox</span>',
    off: '<span class="sandbox-badge bad">⏸️ Test-runner tắt</span>',
  }[r.sandbox] || '';

  if (!r.ran) {
    return `<div class="coach-integrity-fail">
      <strong>🧪 CHƯA CHẠY ĐƯỢC TEST</strong> ${sandboxBadge}
      <p>${escapeHtml(r.reason || 'không rõ lý do')}</p>
      <p><strong>Chưa có test nào chạy thì chưa thể duyệt repo này</strong> — bạn không có
         bằng chứng nào cho thấy học viên làm theo sẽ thấy test xanh.</p>
    </div>`;
  }

  if (r.timedOut) {
    return `<div class="coach-integrity-fail">
      <strong>🧪 CHẠY TEST BỊ TREO</strong> ${sandboxBadge}
      <p>${escapeHtml(r.output || '')} Nhiều khả năng repo có vòng lặp thiếu điều kiện dừng.</p>
    </div>`;
  }

  const allPassed = r.returncode === 0 && r.passed > 0;
  const cases = r.cases || [];
  const logId = `testlog-${p.id}`;

  return `
    <div class="${allPassed ? 'coach-integrity-ok' : 'coach-integrity-fail'}">
      <strong>${allPassed
        ? `🧪 ĐÃ CHẠY THẬT — ${r.passed}/${r.total} TEST PASS`
        : `🧪 REPO KHÔNG PASS TEST — ${r.passed || 0} pass, ${failedCount(r)} fail`}</strong>
      ${sandboxBadge}
      <p>${allPassed
        ? 'Đây là kết quả thực thi thật trong container cách ly, không phải lời hứa của AI. Học viên làm theo tutorial sẽ thấy đúng kết quả này.'
        : 'Học viên làm theo sẽ không bao giờ thấy test xanh. Hãy sửa trong File Explorer rồi bấm <em>Chạy lại test</em>, hoặc sinh lại repo.'}</p>
      ${r.sandboxWarning ? `<p class="sandbox-warn">${escapeHtml(r.sandboxWarning)}</p>` : ''}

      ${cases.length ? `
        <div class="test-case-list">
          ${cases.map(c => `
            <div class="test-case ${c.outcome === 'PASSED' ? 'pass' : 'fail'}">
              <span class="test-case-mark">${c.outcome === 'PASSED' ? '✓' : '✗'}</span>
              <span class="test-case-file">${escapeHtml(c.file)}</span>
              <span class="test-case-name">${escapeHtml(c.test)}</span>
            </div>`).join('')}
        </div>` : ''}

      <button class="link-btn" onclick="toggleTestLog('${logId}')">
        ▸ Xem toàn bộ log terminal
      </button>
      <div id="${logId}" class="test-log-wrap" style="display:none;">
        <div class="test-log-cmd">$ ${escapeHtml(r.command || 'pytest -v')}</div>
        <pre class="test-output">${escapeHtml(r.fullOutput || r.output || '')}</pre>
      </div>
    </div>`;
}

window.toggleTestLog = function (id) {
  const el = document.getElementById(id);
  if (el) el.style.display = el.style.display === 'none' ? 'block' : 'none';
};

function renderAuditPanel(p) {
  const log = p.auditLog || [];
  const failed = p.selfCorrectionFailed || [];

  if (failed.length) {
    return `
      <div class="coach-integrity-fail">
        <strong>🚫 Lõi AI đã tự sửa ${log.length} vòng nhưng VẪN vi phạm ${failed.length} ràng buộc.</strong>
        <p>Nội dung dưới đây <strong>chưa đạt chuẩn của lớp</strong>. Bạn nên sửa tay trong File Explorer,
           hoặc sinh lại với model mạnh hơn (đổi <code>OPENAI_MODEL</code> trong <code>.env</code>).</p>
        <ul>${failed.slice(0, 10).map(x => `<li>${escapeHtml(x)}</li>`).join('')}</ul>
      </div>`;
  }

  if (log.length > 1) {
    const fixed = log.slice(0, -1).reduce((a, r) => a + (r.violations || []).length, 0);
    return `
      <div class="coach-quality-warn">
        <strong>🔁 Lõi AI phải tự sửa ${log.length - 1} vòng mới đạt</strong>
        <p>Lần đầu nó vi phạm ${fixed} ràng buộc; hệ thống trả lỗi ngược lại và bắt sinh lại
           cho tới khi đạt. Kết quả cuối cùng bạn đang xem <strong>đã qua mọi kiểm tra tự động</strong>.</p>
        <p>Phải sửa nhiều vòng nghĩa là <strong>tốn gấp ${log.length} lần token</strong>.
           Nếu việc này lặp lại thường xuyên, nâng model sẽ RẺ HƠN chứ không đắt hơn.</p>
        ${renderUsageLine(p)}
      </div>`;
  }

  if (log.length === 1) {
    return `<div class="coach-integrity-ok">
      ✅ <strong>Lõi AI đạt mọi ràng buộc ngay vòng đầu.</strong>
      ${renderUsageLine(p)}
    </div>`;
  }

  return '';
}

function renderSummaryPanel(p) {
  const s = p.summary || {};
  return `
    <div class="summary-panel">
      <h3 class="summary-h">📄 Tóm tắt bài lab</h3>

      <div class="summary-block">
        <div class="summary-label">Mục tiêu</div>
        <p>${escapeHtml(s.objective || p.description || '')}</p>
      </div>

      ${(s.architecture || []).length ? `
        <div class="summary-block">
          <div class="summary-label">Kiến trúc</div>
          <ul>${s.architecture.map(a => `<li>${escapeHtml(a)}</li>`).join('')}</ul>
        </div>` : ''}

      ${(p.learningGoals || []).length ? `
        <div class="summary-block">
          <div class="summary-label">Học viên sẽ nắm được</div>
          <ul>${p.learningGoals.map(g => `<li>${escapeHtml(g)}</li>`).join('')}</ul>
        </div>` : ''}

      ${(s.testPlan || {}).files ? `
        <div class="summary-block">
          <div class="summary-label">Bộ test (${s.testPlan.total} test — cho sẵn ở Bước 0)</div>
          <ul>${s.testPlan.files.map(f => `<li><code>${escapeHtml(f)}</code></li>`).join('')}</ul>
        </div>` : ''}

      ${(s.risks || []).length ? `
        <div class="summary-block">
          <div class="summary-label">Giới hạn cần nói rõ với học viên</div>
          <ul>${s.risks.map(r => `<li>${escapeHtml(r)}</li>`).join('')}</ul>
        </div>` : ''}

      <div class="summary-block">
        <div class="summary-label">Bộ khung khởi động học viên tải ở Bước 0 (${(p.starterKit || []).length} file)</div>
        <div class="kit-chips">${(p.starterKit || []).map(f => `<code>${escapeHtml(f)}</code>`).join('')}</div>
      </div>
    </div>
  `;
}

function renderTutorialReview(p) {
  const problems = p.integrityProblems || [];
  const warnings = p.qualityWarnings || [];
  const thin = p.explanationProblems || [];
  const blocked = problems.length > 0;

  return `
    <div class="coach-review-card">
      <div class="coach-review-head">
        <div>
          <span class="status-badge st-tutorial">📖 CHỜ DUYỆT TUTORIAL</span>
          <h2 class="coach-review-title">${escapeHtml(p.title)}</h2>
          <p class="coach-review-meta">
            ${(p.steps || []).length - 1} phase (+ Bước 0) · ${escapeHtml(p.duration || '')}
            · ${countLogicLines(p)} dòng học viên tự gõ
          </p>
        </div>
        <div class="coach-review-actions">
          <button class="btn-secondary" onclick="openCodelabWorkspace('${p.id}')">👁️ Xem trước như học viên</button>
          <button class="btn-secondary" onclick="openExplorer('${p.id}')">🗂️ Mở repo</button>
          <button class="btn-secondary" onclick="regenerateTutorial('${p.id}')">🔄 Sinh lại tutorial</button>
          <button class="btn-primary" ${blocked ? 'disabled title="Còn sai lệch giữa tutorial và repo"' : ''}
                  onclick="publishProject('${p.id}')">🚀 Duyệt &amp; Phát hành</button>
        </div>
      </div>

      ${blocked ? `
        <div class="coach-integrity-fail">
          <strong>🚫 CHẶN PHÁT HÀNH — tutorial không khớp repo ở ${problems.length} chỗ.</strong>
          <p>Làm theo tutorial này sẽ KHÔNG ra đúng repo đã duyệt. Bấm
             <em>Đồng bộ tutorial theo repo</em> để ép nội dung code về đúng file trong repo,
             hoặc <em>Sinh lại tutorial</em>.</p>
          <ul>${problems.slice(0, 12).map(x => `<li>${escapeHtml(x)}</li>`).join('')}</ul>
          <button class="btn-primary" style="width:auto;" onclick="syncTutorial('${p.id}')">
            🔧 Đồng bộ tutorial theo repo
          </button>
        </div>
      ` : `
        <div class="coach-integrity-ok">
          ✅ <strong>Đã kiểm chứng:</strong> mọi đoạn code trong tutorial trùng khít từng ký tự với repo đã duyệt.
          Học viên gõ theo sẽ ra đúng repo này và pass toàn bộ test.
        </div>
      `}

      ${p.generatedFromFailingTests ? `
        <div class="coach-thin-warn">
          <strong>⚠️ Tutorial này được sinh khi repo còn test ĐỎ
            (${p.generatedFromFailingTests.passed}/${p.generatedFromFailingTests.total})</strong>
          <p>Bạn đã xác nhận chấp nhận điều đó. Nhưng học viên làm theo tutorial này
             <strong>sẽ không thấy test xanh</strong> cho tới khi repo được sửa.
             Hãy mở File Explorer sửa repo rồi bấm <em>🧪 Chạy lại test</em> trước khi phát hành.</p>
        </div>` : ''}

      ${renderAuditPanel(p)}

      ${thin.length ? `
        <div class="coach-thin-warn">
          <strong>📖 Giải thích quá mỏng ở ${thin.length} bước</strong>
          <p>Luật của lớp: <strong>cứ 4 dòng code phải có ít nhất 1 dòng giải thích</strong>.
             Học viên là người mới — code không kèm lời giảng thì chỉ là chép chính tả.
             Hãy mở bước tương ứng bên dưới và viết thêm phần giải thích.</p>
          <ul>${thin.map(x => `<li>${escapeHtml(x)}</li>`).join('')}</ul>
        </div>` : `
        <div class="coach-integrity-ok">
          📖 <strong>Mật độ giải thích đạt chuẩn:</strong> mọi bước đều có ít nhất 1 dòng giải thích
          cho mỗi 4 dòng code.
        </div>`}

      ${warnings.length ? `
        <div class="coach-quality-warn">
          <strong>⚠️ Lưu ý chất lượng:</strong>
          <ul>${warnings.map(w => `<li>${escapeHtml(w)}</li>`).join('')}</ul>
        </div>` : ''}

      <div class="coach-edit-grid">
        <div class="form-group">
          <label class="form-label">Tên Mini Codelab</label>
          <input class="form-control" value="${escapeHtml(p.title || '')}" oninput="editProject('${p.id}','title',this.value)">
        </div>
        <div class="form-group">
          <label class="form-label">Chuẩn bị cho lab chiều</label>
          <input class="form-control" value="${escapeHtml(p.afternoonLabTarget || '')}" oninput="editProject('${p.id}','afternoonLabTarget',this.value)">
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Mô tả ngắn</label>
        <textarea class="form-control" rows="2" oninput="editProject('${p.id}','description',this.value)">${escapeHtml(p.description || '')}</textarea>
      </div>

      <h3 class="coach-section-title">Nội dung ${(p.steps || []).length} bước</h3>
      ${(p.steps || []).map((s, si) => renderStepEditor(p, s, si)).join('')}
    </div>
  `;
}

function renderStepEditor(p, step, si) {
  const open = state.openStepEditor === `${p.id}:${si}`;
  const m = measureStepBalance(step);
  const thinStep = m.codeLines > 0 && m.explainLines < m.required;
  return `
    <div class="coach-step-editor ${thinStep ? 'is-thin' : ''}">
      <div class="coach-step-head" onclick="toggleStepEditor('${p.id}:${si}')">
        <span class="coach-step-num">${step.num}</span>
        <span class="coach-step-name">${escapeHtml(step.title || '')}</span>
        ${m.codeLines ? `<span class="ratio-pill ${thinStep ? 'bad' : 'good'}"
              title="Mỗi 4 dòng code cần ≥1 dòng giải thích">
          ${m.codeLines} code / ${m.explainLines} giải thích${thinStep ? ` · cần ≥${m.required}` : ''}
        </span>` : ''}
        <span class="coach-step-min">~${step.estimatedMinutes || 0}'</span>
        <span class="coach-step-toggle">${open ? '▲' : '▼'}</span>
      </div>
      ${open ? `
        <div class="coach-step-body">
          <div class="form-group">
            <label class="form-label">Tiêu đề bước</label>
            <input class="form-control" value="${escapeHtml(step.title || '')}"
                   oninput="editStep('${p.id}',${si},'title',this.value)">
          </div>
          ${(step.blocks || []).map((b, bi) => renderBlockEditor(p, b, si, bi)).join('')}
        </div>` : ''}
    </div>
  `;
}

function renderBlockEditor(p, block, si, bi) {
  const label = {
    text: '📝 Đoạn giải thích',
    code: '💻 Code / lệnh',
    tree: '🗂️ Cây thư mục',
    callout: '💡 Ghi chú nổi bật',
    checklist: '✓ Checklist tự kiểm',
    quiz: '❓ Câu hỏi củng cố',
  }[block.type] || block.type;

  // Code có filename = nội dung file trong repo -> chỉ sửa được trong File Explorer,
  // sửa ở hai nơi sẽ làm tutorial và repo trôi khỏi nhau.
  if (block.type === 'code' && block.filename) {
    return `
      <div class="coach-block-editor">
        <div class="coach-block-head">
          <span>${label} · <code>${escapeHtml(block.filename)}</code></span>
          <span class="locked-tag">🔒 khoá theo repo</span>
        </div>
        <p class="locked-hint">
          Nội dung này luôn bằng file trong repo. Muốn sửa, hãy
          <a href="#" onclick="event.preventDefault(); openExplorer('${p.id}','${escapeHtml(block.filename)}')">mở file trong repo</a>.
        </p>
        <pre class="locked-preview">${escapeHtml((block.content || '').split('\n').slice(0, 6).join('\n'))}${(block.content || '').split('\n').length > 6 ? '\n…' : ''}</pre>
      </div>`;
  }

  let body;
  if (block.type === 'tree' || block.type === 'checklist') {
    body = `<textarea class="form-control code-edit" rows="5"
              oninput="editBlockLines('${p.id}',${si},${bi},'items',this.value)">${escapeHtml((block.items || []).join('\n'))}</textarea>`;
  } else if (block.type === 'quiz') {
    body = `
      <div class="form-group">
        <label class="form-label">Câu hỏi</label>
        <textarea class="form-control" rows="2" oninput="editBlock('${p.id}',${si},${bi},'question',this.value)">${escapeHtml(block.question || '')}</textarea>
      </div>
      ${(block.options || []).map((o, oi) => `
        <div class="form-group">
          <label class="form-label">Đáp án ${String.fromCharCode(65 + oi)}${block.correct === oi ? ' (ĐÚNG)' : ''}</label>
          <input class="form-control" value="${escapeHtml(o)}" oninput="editOption('${p.id}',${si},${bi},${oi},this.value)">
        </div>`).join('')}
      <div class="form-group">
        <label class="form-label">Giải thích</label>
        <textarea class="form-control" rows="2" oninput="editBlock('${p.id}',${si},${bi},'explanation',this.value)">${escapeHtml(block.explanation || '')}</textarea>
      </div>`;
  } else {
    body = `<textarea class="form-control code-edit" rows="4"
              oninput="editBlock('${p.id}',${si},${bi},'content',this.value)">${escapeHtml(block.content || '')}</textarea>`;
  }

  return `
    <div class="coach-block-editor">
      <div class="coach-block-head">
        <span>${label}</span>
        <button class="coach-block-del" onclick="deleteBlock('${p.id}',${si},${bi})" title="Xoá khối này">✕</button>
      </div>
      ${body}
    </div>`;
}
