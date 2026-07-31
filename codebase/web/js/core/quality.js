// Chốt chặn chất lượng phía trình duyệt.
//
// Hai luật bất di bất dịch, kiểm lại sau MỌI thao tác sửa:
//   1. Mỗi block code trong tutorial phải trùng khít file trong repo (từng ký tự).
//   2. Mỗi 4 dòng code phải có ít nhất 1 dòng giải thích.
// Giao diện khoá nút Phát hành khi luật 1 bị vi phạm.

function checkIntegrity(project) {
  const byPath = {};
  repoFiles(project).forEach(f => { byPath[f.path] = f.content || ''; });

  const kit = new Set(project.starterKit || []);
  const covered = new Set();
  const problems = [];

  (project.steps || []).forEach(step => {
    (step.blocks || []).forEach(block => {
      if (block.type !== 'code' || !block.filename) return;
      const path = block.filename;
      if (!(path in byPath)) {
        problems.push(`Bước ${step.num}: tutorial dạy file "${path}" nhưng repo không có file này.`);
        return;
      }
      // Đã được tutorial nhắc tới thì coi là "có dạy", kể cả khi nội dung còn lệch —
      // nếu không sẽ báo thêm lỗi "chưa dạy file này" gây hiểu nhầm.
      covered.add(path);
      if ((block.content || '') !== byPath[path]) {
        problems.push(`Bước ${step.num}: nội dung "${path}" trong tutorial LỆCH với file trong repo.`);
      }
    });
  });

  Object.keys(byPath).forEach(path => {
    if (!covered.has(path) && !kit.has(path)) {
      problems.push(`File "${path}" có trong repo nhưng không nằm trong bộ khung khởi động lẫn tutorial — học viên sẽ không bao giờ tạo được nó.`);
    }
  });

  project.integrityProblems = problems;
  checkExplanationRatio(project);
  return problems;
}

// ---------------------------------------------------------------------------
// Chốt chặn: mỗi 4 dòng code phải có ít nhất 1 dòng giải thích
// Đây là app cho người MỚI — code không kèm lời giải thích chỉ là chép chính tả.
// ---------------------------------------------------------------------------
const MIN_EXPLANATION_RATIO = 4;
const CHARS_PER_EXPLANATION_LINE = 80;

function stripHtml(html) {
  return (html || '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(p|li|ul|ol|div)>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .split(/\s+/).filter(Boolean).join(' ');
}

function explanationLines(html) {
  const plain = stripHtml(html);
  return plain ? Math.ceil(plain.length / CHARS_PER_EXPLANATION_LINE) : 0;
}

// Khối 'text' và 'callout' tính là giảng; 'checklist' và 'quiz' là kiểm tra nên không tính.
function measureStepBalance(step) {
  let codeLines = 0;
  let explainLines = 0;

  (step.blocks || []).forEach(b => {
    if (b.type === 'code' && b.filename) {
      codeLines += (b.content || '').split('\n').length;
    } else if (b.type === 'text' || b.type === 'callout') {
      explainLines += explanationLines(b.content);
    }
  });

  return { codeLines, explainLines, required: Math.ceil(codeLines / MIN_EXPLANATION_RATIO) };
}

function checkExplanationRatio(project) {
  const problems = [];
  (project.steps || []).forEach(step => {
    const m = measureStepBalance(step);
    if (m.codeLines && m.explainLines < m.required) {
      problems.push(`Bước ${step.num} (${(step.title || '').slice(0, 40)}): ${m.codeLines} dòng code nhưng chỉ ${m.explainLines} dòng giải thích — cần tối thiểu ${m.required}.`);
    }
  });
  project.explanationProblems = problems;
  return problems;
}

// Ép nội dung tutorial về đúng repo (dùng khi Coach vừa sửa file trong Explorer).
function syncTutorialToRepo(project) {
  const byPath = {};
  repoFiles(project).forEach(f => { byPath[f.path] = f.content || ''; });

  let fixed = 0;
  (project.steps || []).forEach(step => {
    (step.blocks || []).forEach(block => {
      if (block.type === 'code' && block.filename && block.filename in byPath) {
        if ((block.content || '') !== byPath[block.filename]) {
          block.content = byPath[block.filename];
          fixed++;
        }
      }
    });
  });
  checkIntegrity(project);
  return fixed;
}
