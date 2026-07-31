// Vai HỌC VIÊN — chỉ nhìn thấy bài đã được Coach phát hành.

// ---------------------------------------------------------------------------
// HỌC VIÊN — chỉ nhìn thấy bài đã phát hành
// ---------------------------------------------------------------------------
function renderStudentDashboard() {
  const published = state.projects.filter(p => p.status === 'published');

  return `
    <div class="section-header">
      <div>
        <div class="breadcrumb-tag">VLEARN • VINUNI AI THỰC CHIẾN</div>
        <h1 class="page-title">Mini Codelab buổi sáng</h1>
        <p class="page-subtitle">
          Làm trước giờ lab chiều 4 tiếng. Bạn đọc cẩm nang ở đây, tự gõ code trong IDE và chạy trên máy mình.
        </p>
      </div>
      <div class="course-count-badge">${published.length} bài đang mở</div>
    </div>

    ${published.length === 0 ? `
      <div class="empty-state">
        <div class="empty-state-icon">📭</div>
        <p>Chưa có Mini Codelab nào được phát hành.</p>
        <p class="empty-state-sub">Lab Coach cần duyệt repo và tutorial trước khi bạn nhìn thấy ở đây.</p>
      </div>
    ` : `
      <div class="codelabs-grid">
        ${published.map(lab => `
          <div class="codelab-item-card">
            <div>
              <div class="codelab-card-tag">
                <span class="tag-morning">${escapeHtml(lab.morningTopic)}</span>
                <span class="tag-duration">⏱️ ${escapeHtml(lab.duration)}</span>
              </div>
              <h3 class="codelab-card-h3">${escapeHtml(lab.title)}</h3>
              <p class="codelab-card-desc">${escapeHtml(lab.description)}</p>

              <div class="lab-facts">
                <span>${(lab.steps || []).length - 1} phase</span>
                <span>${repoFiles(lab).length} file</span>
                <span>${countLogicLines(lab)} dòng bạn tự gõ</span>
                <span>${((lab.summary || {}).testPlan || {}).total || 0} test</span>
              </div>

              ${(lab.learningGoals || []).length ? `
                <div class="lab-goals">
                  <div class="lab-goals-title">Bạn sẽ nắm được</div>
                  <ul>${lab.learningGoals.slice(0, 5).map(g => `<li>${escapeHtml(g)}</li>`).join('')}</ul>
                </div>` : ''}

              <div class="codelab-card-meta">
                <strong>Nguồn lý thuyết:</strong> ${escapeHtml(lab.morningSlideRef)}<br>
                <strong>Chuẩn bị cho:</strong> ${escapeHtml(lab.afternoonLabTarget)}
              </div>
            </div>
            <button class="btn-primary" onclick="openCodelabWorkspace('${lab.id}')">
              <span>Bắt đầu làm</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            </button>
          </div>
        `).join('')}
      </div>
    `}
  `;
}
