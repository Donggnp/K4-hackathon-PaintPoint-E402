// Tiện ích thuần: không đụng tới DOM, không gọi mạng.

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function pad2(n) { return String(n).padStart(2, '0'); }

function formatTimer(totalSeconds) {
  totalSeconds = Math.max(0, totalSeconds | 0);
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  return h > 0 ? `${pad2(h)}:${pad2(m)}:${pad2(s)}` : `${pad2(m)}:${pad2(s)}`;
}

function parseDurationMinutes(durationStr) {
  const m = /(\d+)/.exec(durationStr || '');
  return m ? parseInt(m[1], 10) : 40;
}

function findProject(id) {
  return state.projects.find(p => p.id === id) || null;
}

function repoFiles(project) {
  return ((project || {}).repo || {}).files || [];
}

function isStarterKitPath(project, path) {
  return (project.starterKit || []).indexOf(path) >= 0;
}

function countLogicLines(project) {
  return repoFiles(project)
    .filter(f => !isStarterKitPath(project, f.path))
    .reduce((sum, f) => sum + (f.content || '').split('\n').length, 0);
}
