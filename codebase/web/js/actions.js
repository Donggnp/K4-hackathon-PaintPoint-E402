// Vòng đời mini-project: sinh, duyệt, phát hành, xoá.

// ---------------------------------------------------------------------------
// Vòng đời mini-project
// ---------------------------------------------------------------------------
function recomputeDuration(p) {
  const LINES_PER_MINUTE = 22;
  const byPath = {};
  repoFiles(p).forEach(f => { byPath[f.path] = f.content || ''; });

  let total = 0;
  (p.steps || []).forEach((step, i) => {
    step.num = i;
    let lines = 0;
    (step.blocks || []).forEach(b => {
      if (b.type === 'code' && b.filename && b.filename in byPath) {
        lines += byPath[b.filename].split('\n').length;
      }
    });
    step.estimatedMinutes = lines === 0
      ? Math.max(3, Number(step.estimatedMinutes) || 4)
      : Math.max(3, Math.ceil(lines / LINES_PER_MINUTE + 2));
    total += step.estimatedMinutes;
  });

  if (total > 0) p.duration = `${total} phút`;
  return total;
}

// Việc sinh bài chạy ở luồng nền trên server. Ta hỏi tiến độ mỗi 2 giây và
// hiện ra màn hình, thay vì để người dùng nhìn một vòng xoay im lặng vài phút.
async function waitForJob(jobId, onProgress) {
  while (true) {
    await new Promise(r => setTimeout(r, 2000));

    let data;
    try {
      data = await (await fetch(`/api/job/${jobId}`)).json();
    } catch (err) {
      continue;                       // mạng chớp nháy thì thử lại, đừng bỏ cuộc
    }

    if (!data.success) throw new Error(data.error || 'Mất dấu job');

    const job = data.job;
    if (onProgress) onProgress(job);

    if (job.status === 'done') return job.result;
    if (job.status === 'error') throw new Error(job.error || 'Job lỗi');
  }
}

function formatElapsed(seconds) {
  const s = Math.round(seconds || 0);
  return s < 60 ? `${s}s` : `${Math.floor(s / 60)}m ${String(s % 60).padStart(2, '0')}s`;
}

// Coach chọn mô tả lab chiều bằng README.md hay cả repo .zip.
window.setLabSource = function (kind) {
  state.labSource = kind;
  renderApp();
};

// Gom đầu vào của form thành payload gửi server. Tách riêng để phần xử lý
// bên dưới không phải quan tâm Coach đã chọn cách nào.
async function collectRepoSourcePayload() {
  const pdfInput = document.getElementById('coach-slide-pdf');
  if (!pdfInput || !pdfInput.files[0]) {
    return { error: 'Thiếu Slide PDF buổi sáng — đây là nguồn lý thuyết bắt buộc.' };
  }

  const payload = {
    pdf_base64: await fileToBase64(pdfInput.files[0]),
    pdf_filename: pdfInput.files[0].name,
    source_kind: state.labSource,
  };

  if (state.labSource === 'readme') {
    const fileInput = document.getElementById('coach-readme-file');
    const textInput = document.getElementById('coach-readme-text');
    const typed = (textInput && textInput.value || '').trim();

    if (fileInput && fileInput.files[0]) {
      payload.readme_base64 = await fileToBase64(fileInput.files[0]);
      payload.readme_filename = fileInput.files[0].name;
    } else if (typed) {
      payload.readme_text = typed;
      payload.readme_filename = 'README.md';
    } else {
      return { error: 'Thiếu README.md — chọn file, hoặc dán nội dung vào ô bên dưới.' };
    }
  } else {
    const zipInput = document.getElementById('coach-repo-zip');
    if (!zipInput || !zipInput.files[0]) {
      return { error: 'Thiếu file .zip của repo lab chiều.' };
    }
    payload.zip_base64 = await fileToBase64(zipInput.files[0]);
    payload.zip_filename = zipInput.files[0].name;
  }

  return { payload };
}

window.handleGenerateRepo = async function () {
  const rules = document.getElementById('coach-prompt-rules').value;
  const box = document.getElementById('coach-generation-progress');
  const btn = document.getElementById('btn-generate-repo');

  box.style.display = 'block';

  const collected = await collectRepoSourcePayload();
  if (collected.error) {
    box.innerHTML = `<div class="gen-error"><strong>❌ Thiếu đầu vào:</strong> ${escapeHtml(collected.error)}</div>`;
    return;
  }

  const sourceLabel = state.labSource === 'readme' ? 'README.md' : 'repo .zip';
  btn.disabled = true;
  box.innerHTML = `
    <h4 class="gen-title">🤖 Đang sinh repo mini-project...</h4>
    <div class="progress-step-item active"><div class="progress-step-icon">1</div><span>Đọc Slide PDF theo trang + ${escapeHtml(sourceLabel)} của lab chiều</span></div>
    <div class="progress-step-item"><div class="progress-step-icon">2</div><span>Lõi sinh repo hoàn chỉnh, rồi CHẠY THẬT pytest (có thể mất vài phút)</span></div>
    <div class="progress-step-item"><div class="progress-step-icon">3</div><span>Tự kiểm quy mô, bảo mật, tách bộ khung khởi động</span></div>`;

  try {
    const started = await (await fetch('/api/generate_repo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(Object.assign({ rules }, collected.payload)),
    })).json();

    if (!started.success) {
      box.innerHTML = `<div class="gen-error">
        <strong>❌ Không sinh được repo:</strong><br>${escapeHtml(started.error || 'Lỗi không xác định')}
        ${started.hint ? `<br><br>💡 ${escapeHtml(started.hint)}` : ''}</div>`;
      return;
    }

    const data = await waitForJob(started.jobId, job => {
      const pr = job.progress || {};
      box.innerHTML = `
        <div class="gen-live">
          <div class="gen-spinner"></div>
          <div class="gen-live-body">
            <h4 class="gen-title">Đang sinh repo mini-project
              <span class="gen-elapsed">${formatElapsed(job.elapsed)}</span></h4>
            <div class="gen-phase">${escapeHtml(pr.phase || '')}</div>
            ${pr.totalRounds ? `<div class="gen-rounds">Vòng ${pr.round}/${pr.totalRounds}</div>` : ''}
            ${(pr.detail || []).length ? `
              <ul class="gen-detail">${pr.detail.map(d => `<li>${escapeHtml(String(d).slice(0, 160))}</li>`).join('')}</ul>` : ''}
            <p class="gen-note">Lõi viết code, rồi hệ thống chạy test thật trong Docker.
               Test đỏ thì nó phải sửa lại. Thường mất 30-90 giây.</p>
          </div>
        </div>`;
    });

    const p = data.lab;
    p.id = `lab-${Date.now()}`;
    p.status = 'repo_review';
    p.auditLog = data.auditLog || [];
    p.usage = data.usage || null;
    p.testReport = data.lab.testReport || null;
    state.projects.unshift(p);

    const meta = data.extraction_meta || {};
    renderApp();
    setTimeout(() => {
      const el = document.querySelector('.coach-review-card');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 80);
    const rounds = (data.auditLog || []).length;
    alert(
      `✅ Đã sinh repo "${p.repoName}" gồm ${repoFiles(p).length} file (${countLogicLines(p)} dòng logic).\n` +
      (rounds > 1 ? `Lõi AI phải tự sửa ${rounds - 1} vòng mới đạt ràng buộc.\n` : `Đạt ràng buộc ngay vòng đầu.\n`) +
      `\n` +
      `Slide: dùng ${meta.slide_pages_used}/${meta.slide_pages_total} trang có text.\n` +
      (meta.source_kind === 'readme'
        ? `Lab chiều: đọc từ README.md.\n\n`
        : `Lab chiều: đọc ${meta.repo_files_found} file từ repo .zip.\n\n`) +
      `Bước tiếp theo: mở repo, soát code, rồi bấm "Duyệt repo & sinh tutorial".`
    );
  } catch (err) {
    box.innerHTML = `<div class="gen-error"><strong>❌ Lỗi kết nối server:</strong> ${escapeHtml(err.message)}</div>`;
  } finally {
    btn.disabled = false;
  }
};

async function requestTutorial(p, onProgress, allowFailingTests = false) {
  const started = await (await fetch('/api/generate_tutorial', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lab: p, allowFailingTests }),
  })).json();
  if (!started.success) throw new Error(started.error || 'Không sinh được tutorial');

  const data = await waitForJob(started.jobId, onProgress);

  Object.assign(p, data.lab);
  p.status = 'tutorial_review';
  p.auditLog = data.auditLog || [];
  p.usage = data.usage || null;
  syncTutorialToRepo(p);
  recomputeDuration(p);
  checkIntegrity(p);
  return data.repairedBlocks || [];
}

window.approveRepoAndGenerateTutorial = async function (projectId) {
  const p = findProject(projectId);
  if (!p || state.busy) return;

  // Test chưa xanh thì CẢNH BÁO và hỏi lại, không chặn — Coach là người quyết định.
  // Nhưng phải nói rõ hậu quả, đừng để họ bấm qua mà không biết mình đang chấp nhận gì.
  let allowFailingTests = false;
  if (!testsGreen(p)) {
    const r = p.testReport || {};
    const ok = confirm(
      '⚠️ REPO CHƯA PASS HẾT TEST\n\n' +
      (r.ran
        ? `Mới pass ${r.passed || 0}/${r.total || 0} test trong sandbox.`
        : `Test chưa chạy được: ${r.reason || 'chưa rõ'}`) +
      '\n\nNếu vẫn sinh tutorial, học viên làm theo sẽ KHÔNG thấy test xanh — trừ khi ' +
      'bạn sửa repo trước lúc phát hành.\n\n' +
      'Bạn vẫn muốn sinh tutorial chứ?\n' +
      '(Hệ thống sẽ ghi dấu bài này là "sinh từ repo test đỏ".)'
    );
    if (!ok) return;
    allowFailingTests = true;
  }

  if (!confirm(
    `Duyệt repo "${p.repoName}" và cho AI viết tutorial?\n\n` +
    `Tutorial sẽ được sinh TỪ ĐÚNG repo này. Sau đó bạn vẫn duyệt tutorial lần nữa trước khi phát hành.`
  )) return;

  state.busy = true;
  const busy = showBusy('🤖 Đang viết tutorial step-by-step từ repo đã duyệt...');
  const done = busy.close;
  try {
    const repaired = await requestTutorial(p, job => busy.update(job), allowFailingTests);
    done();
    renderApp();
    alert(
      `✅ Đã sinh tutorial: ${(p.steps || []).length - 1} phase + Bước 0, tổng ${p.duration}.\n` +
      (repaired.length ? `\nHệ thống đã tự sửa ${repaired.length} đoạn code bị AI chép lệch về đúng nội dung repo.\n` : '') +
      `\nHãy xem trước rồi bấm "Duyệt & Phát hành".`
    );
  } catch (err) {
    done();
    alert('❌ ' + err.message);
  } finally {
    state.busy = false;
  }
};

window.regenerateTutorial = async function (projectId) {
  const p = findProject(projectId);
  if (!p || state.busy) return;
  if (!confirm('Sinh lại tutorial từ repo hiện tại? Nội dung tutorial cũ sẽ bị thay thế.')) return;

  state.busy = true;
  const busy = showBusy('🔄 Đang sinh lại tutorial...');
  const done = busy.close;
  try {
    await requestTutorial(p, job => busy.update(job), !testsGreen(p));
    done();
    renderApp();
  } catch (err) {
    done();
    alert('❌ ' + err.message);
  } finally {
    state.busy = false;
  }
};

// Coach sửa repo xong -> chạy lại pytest thật để biết còn xanh không.
window.rerunTests = async function (projectId) {
  const p = findProject(projectId);
  if (!p || state.busy) return;

  state.busy = true;
  const done = showBusy('🧪 Đang chạy pytest thật trong sandbox Docker...').close;
  try {
    const res = await fetch('/api/verify_lab', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lab: p, run_tests: true }),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || 'Không chạy được test');

    p.testReport = data.testReport || null;
    done();
    renderApp();

    const r = p.testReport || {};
    if (!r.ran) alert('Chưa chạy được test: ' + (r.reason || 'không rõ'));
    else if (r.timedOut) alert('⏱️ Test bị treo — nghi có vòng lặp vô hạn.');
    else if (r.returncode === 0) alert(`✅ ${r.passed} test PASS.`);
    else alert(`❌ ${r.passed} pass, ${r.failed} fail. Xem chi tiết ở khung báo cáo.`);
  } catch (err) {
    done();
    alert('❌ ' + err.message);
  } finally {
    state.busy = false;
  }
};

window.syncTutorial = function (projectId) {
  const p = findProject(projectId);
  if (!p) return;
  const fixed = syncTutorialToRepo(p);
  recomputeDuration(p);
  renderApp();
  const left = (p.integrityProblems || []).length;
  alert(left
    ? `Đã ép ${fixed} đoạn code về đúng repo, nhưng còn ${left} vấn đề về cấu trúc (file thừa/thiếu). Nên bấm "Sinh lại tutorial".`
    : `✅ Đã đồng bộ ${fixed} đoạn code. Tutorial giờ khớp repo 100%.`);
};

window.publishProject = function (projectId) {
  const p = findProject(projectId);
  if (!p) return;

  const problems = checkIntegrity(p);
  if (problems.length) {
    alert(`🚫 Không thể phát hành: tutorial còn lệch repo ở ${problems.length} chỗ.`);
    renderApp();
    return;
  }

  p.status = 'published';
  p.repoStatus = 'approved';
  state.openStepEditor = null;
  renderApp();
  alert(`🚀 Đã phát hành "${p.title}". Học viên đã nhìn thấy bài này.`);
};

window.unpublishProject = function (projectId) {
  const p = findProject(projectId);
  if (!p) return;
  if (!confirm(`Gỡ "${p.title}" xuống? Học viên sẽ không còn nhìn thấy bài này.`)) return;
  p.status = 'tutorial_review';
  renderApp();
};

window.deleteProject = function (projectId) {
  const p = findProject(projectId);
  if (!p) return;
  if (!confirm(`Xoá hẳn "${p.title}"?\n\nCả repo lẫn tutorial sẽ mất và không khôi phục được.`)) return;

  state.projects = state.projects.filter(x => x.id !== projectId);
  if (state.explorerProjectId === projectId) state.explorerProjectId = null;
  if (state.activeCodelabId === projectId) state.activeCodelabId = null;
  renderApp();
};

// Lớp phủ "đang xử lý". Trả về {close, update} để việc chạy nền còn báo được
// tiến độ vào đây — vòng xoay im lặng vài phút là thứ khiến người dùng tưởng treo.
function showBusy(message) {
  const overlay = document.createElement('div');
  overlay.className = 'busy-overlay';
  overlay.innerHTML = `<div class="busy-box">
      <div class="busy-spinner"></div>
      <p>${escapeHtml(message)}</p>
      <div class="busy-progress"></div>
    </div>`;
  document.body.appendChild(overlay);

  return {
    close: () => overlay.remove(),
    update: (job) => {
      const box = overlay.querySelector('.busy-progress');
      if (!box) return;
      const pr = (job && job.progress) || {};
      box.innerHTML = `
        <div class="busy-phase">${escapeHtml(pr.phase || '')}</div>
        <div class="busy-elapsed">${formatElapsed(job && job.elapsed)}${
          pr.totalRounds ? ` · vòng ${pr.round}/${pr.totalRounds}` : ''}</div>`;
    },
  };
}

// --- sửa nội dung tutorial (phần không phải code file) ---------------------
window.editProject = function (id, key, value) {
  const p = findProject(id);
  if (p) p[key] = value;
};

window.editStep = function (id, si, key, value) {
  const p = findProject(id);
  if (p && p.steps[si]) p.steps[si][key] = value;
};

window.editBlock = function (id, si, bi, key, value) {
  const p = findProject(id);
  if (!p || !p.steps[si] || !p.steps[si].blocks[bi]) return;
  p.steps[si].blocks[bi][key] = value;
  checkExplanationRatio(p);   // sửa lời giảng -> tỉ lệ đổi theo ngay
};

window.editBlockLines = function (id, si, bi, key, value) {
  const p = findProject(id);
  if (p && p.steps[si] && p.steps[si].blocks[bi]) {
    p.steps[si].blocks[bi][key] = value.split('\n').filter(l => l.trim() !== '');
  }
};

window.editOption = function (id, si, bi, oi, value) {
  const p = findProject(id);
  if (p && p.steps[si] && p.steps[si].blocks[bi]) p.steps[si].blocks[bi].options[oi] = value;
};

window.deleteBlock = function (id, si, bi) {
  const p = findProject(id);
  if (!p) return;
  p.steps[si].blocks.splice(bi, 1);
  checkIntegrity(p);
  renderApp();
};

window.toggleStepEditor = function (key) {
  state.openStepEditor = state.openStepEditor === key ? null : key;
  renderApp();
};


// ---------------------------------------------------------------------------
// Lịch sử lượt chạy — nạp lại bài cũ vào Studio bất cứ lúc nào
// ---------------------------------------------------------------------------
window.reloadRuns = async function () {
  try {
    const data = await (await fetch('/api/runs')).json();
    state.runs = data.runs || [];
    renderApp();
  } catch (err) {
    console.warn('Không đọc được lịch sử:', err);
  }
};

window.restoreRun = async function (runId) {
  if (state.busy) return;
  state.busy = true;
  const done = showBusy('↩️ Đang nạp lại lượt chạy cũ...').close;
  try {
    const data = await (await fetch(`/api/runs/${runId}`)).json();
    if (!data.success) throw new Error(data.error || 'Không nạp được');

    const lab = data.lab;
    // Nạp lại thành một bản nháp MỚI để không đè lên bài đang làm dở.
    lab.id = `lab-${Date.now()}`;
    lab.status = (lab.steps || []).length ? 'tutorial_review' : 'repo_review';
    checkIntegrity(lab);
    state.projects.unshift(lab);

    done();
    renderApp();
    alert(
      `↩️ Đã nạp lại "${lab.title}".\n\n` +
      `${(lab.repo?.files || []).length} file · ${(lab.steps || []).length} bước\n` +
      `Trạng thái: ${lab.status === 'tutorial_review' ? 'chờ duyệt tutorial' : 'chờ duyệt repo'}\n\n` +
      `Bạn có thể sửa, chạy lại test, rồi phát hành như bình thường.`
    );
  } catch (err) {
    done();
    alert('❌ ' + err.message);
  } finally {
    state.busy = false;
  }
};

window.deleteRun = async function (runId) {
  if (!confirm(`Xoá lượt chạy "${runId}"?\n\nCả thư mục repo và tutorial trên đĩa sẽ mất.`)) return;
  try {
    const data = await (await fetch(`/api/runs/delete/${runId}`, { method: 'POST' })).json();
    if (!data.success) throw new Error('Không xoá được');
    await reloadRuns();
  } catch (err) {
    alert('❌ ' + err.message);
  }
};
