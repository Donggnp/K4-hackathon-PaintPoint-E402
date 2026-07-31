// Trạng thái ứng dụng — nguồn sự thật duy nhất cho toàn bộ giao diện.
//
// Luồng nghiệp vụ:
//   1. Coach nạp Slide PDF + mô tả lab chiều (repo .zip HOẶC README.md)
//   2. AI sinh tóm tắt + REPO CODE          -> status 'repo_review'
//   3. Coach sửa repo trong File Explorer, hoặc tải .zip về sửa rồi upload lại
//   4. Coach DUYỆT REPO -> AI mới sinh tutorial -> status 'tutorial_review'
//   5. Coach DUYỆT TUTORIAL -> status 'published', học viên mới nhìn thấy

const STATUS_LABEL = {
  repo_review: { text: '📦 CHỜ DUYỆT REPO', cls: 'st-repo' },
  tutorial_review: { text: '📖 CHỜ DUYỆT TUTORIAL', cls: 'st-tutorial' },
  published: { text: '✅ ĐÃ PHÁT HÀNH', cls: 'st-published' },
};

const state = {
  currentRole: 'student',
  theme: 'light',
  // Bắt đầu RỖNG. Coach tự sinh bài của mình; không có project mẫu nào lẫn vào.
  // (Bài mẫu chỉ tồn tại ở hai chỗ: ví dụ vàng nhúng trong system prompt để dạy
  //  lõi, và tests/fixtures/golden-labs.json để kiểm thử — không hiện lên web.)
  projects: [],

  // Trang cẩm nang (học viên đọc)
  activeCodelabId: null,
  activeStep: 0,
  timerSecondsLeft: 0,
  timerInterval: null,
  checklist: {},

  // Trang File Explorer của Coach
  explorerProjectId: null,
  explorerPath: null,
  collapsedDirs: {},

  // Coach mô tả lab chiều bằng README.md (nhẹ) hay cả repo .zip (nhiều ngữ cảnh).
  labSource: 'readme',

  // Lịch sử lượt chạy, nạp từ /api/runs khi mở Studio.
  runs: [],

  openStepEditor: null,
  busy: false,
};
