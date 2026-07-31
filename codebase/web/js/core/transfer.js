// Tải repo/bộ khung khởi động xuống, và nạp repo đã sửa lên.

// ---------------------------------------------------------------------------
// Tải / nạp repo dưới dạng .zip
// ---------------------------------------------------------------------------
function triggerDownload(base64, filename) {
  const a = document.createElement('a');
  a.href = 'data:application/zip;base64,' + base64;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

async function packAndDownload(files, rootName, onlyPaths) {
  const res = await fetch('/api/pack_repo', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ files, root_name: rootName, only_paths: onlyPaths || null }),
  });
  const data = await res.json();
  if (!data.success) throw new Error(data.error || 'Đóng gói thất bại');
  triggerDownload(data.zip_base64, data.filename);
  return data.file_count;
}

window.downloadRepo = async function (projectId) {
  const p = findProject(projectId);
  if (!p) return;
  try {
    await packAndDownload(repoFiles(p), p.repoName || 'repo');
  } catch (err) {
    alert('Không tải được repo: ' + err.message);
  }
};

window.downloadStarterKit = async function (projectId) {
  const p = findProject(projectId);
  if (!p) return;
  try {
    await packAndDownload(repoFiles(p), `${p.repoName || 'repo'}-starter`, p.starterKit || []);
  } catch (err) {
    alert('Không tải được bộ khung khởi động: ' + err.message);
  }
};

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.substring(reader.result.indexOf(',') + 1));
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

window.uploadRepo = async function (projectId, input) {
  const p = findProject(projectId);
  const file = input.files && input.files[0];
  if (!p || !file) return;

  try {
    const zipBase64 = await fileToBase64(file);
    const res = await fetch('/api/unpack_repo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ zip_base64: zipBase64 }),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    p.repo.files = data.files;
    p.starterKit = data.starter_kit;
    state.explorerPath = null;

    let message = `Đã nạp ${data.files.length} file từ ${file.name}.`;
    if ((p.steps || []).length) {
      const fixed = syncTutorialToRepo(p);
      const problems = checkIntegrity(p);
      message += fixed ? `\nĐã cập nhật ${fixed} đoạn code trong tutorial theo repo mới.` : '';
      if (problems.length) {
        message += `\n\n⚠️ Còn ${problems.length} vấn đề — repo mới có file mà tutorial chưa dạy, hoặc ngược lại. Nên bấm "Sinh lại tutorial".`;
      }
    }
    recomputeDuration(p);
    renderApp();
    alert(message);
  } catch (err) {
    alert('Upload thất bại: ' + err.message);
  } finally {
    input.value = '';
  }
};
