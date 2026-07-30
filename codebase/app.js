// VLearn CP2 - Mini Codelab Application Core Logic

// State Management
const state = {
  currentRole: 'student', // 'student' | 'coach'
  theme: 'light',
  activeCodelabId: null,
  activeStep: 1,
  apiKey: '',
  
  // Data Pack Mini Codelabs
  codelabs: [
    {
      id: 'lab-react-01',
      title: 'Mini Lab 01: ReAct Agent & OpenAI Function Calling',
      morningTopic: 'Buổi 4 - ReAct Agent Architecture & Prompting',
      morningSlideRef: 'Slide 03: ReAct Loop [T04-032]',
      afternoonLabTarget: 'github.com/vlearn/day4-research-agent-lab (4 tiếng)',
      duration: '15 phút',
      status: 'Mới',
      description: 'Thực hành mini ReAct Agent với 1 tool đơn giản trước khi bước vào bài Lab chiều 4 tiếng.',
      steps: [
        {
          num: 1,
          title: 'Hiểu Lý thuyết & Cầu nối',
          content: `
            <div class="theory-bridge-box">
              <div class="theory-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 14l9-5-9-5-9 5 9 5z"/><path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0112 20.055a11.952 11.952 0 01-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/></svg>
                Trích dẫn Lý thuyết Sáng (Slide 03 - ReAct Loop [T04-032])
              </div>
              <div class="theory-content">
                Mô hình <strong>ReAct (Reasoning + Acting)</strong> cho phép AI chia nhỏ bài toán thành các vòng lặp:
                <br><code>Thought (Suy nghĩ) ➔ Action (Gọi tool) ➔ Observation (Kết quả) ➔ Final Answer</code>.
                <br><br>
                <strong>🎯 Tại sao cần cho bài chiều?</strong> Bài lab chiều yêu cầu bạn build Research Agent với 6 tools. 
                Nắm vững vòng lặp 1 tool ở mini lab này sẽ giúp bạn không bị lạc trôi khi gõ prompt bài chiều!
              </div>
            </div>
          `
        },
        {
          num: 2,
          title: 'Thử nghiệm Code & Prompt',
          starterCode: `# Mini ReAct Agent with 1 Tool: lookup_paper
import json

def lookup_paper(query):
    # Simulated search tool
    database = {
        "attention": "Attention Is All You Need (Vaswani et al., 2017) - Intro Transformer",
        "react": "ReAct: Synergizing Reasoning and Acting in LLMs (Yao et al., 2022)"
    }
    return database.get(query.lower(), "Không tìm thấy tài liệu phù hợp.")

# User prompt
user_query = "Tìm cho tôi bài báo về ReAct Agent"

# Step 1: Agent Thought & Action Selection
print("[THOUGHT] Người dùng muốn tìm bài báo về ReAct. Tôi sẽ dùng tool lookup_paper với query='react'")
tool_result = lookup_paper("react")

# Step 2: Agent Observation & Final Answer
print(f"[OBSERVATION] Tool trả về: {tool_result}")
print(f"[FINAL ANSWER] Bài báo bạn cần là: {tool_result}")
`
        },
        {
          num: 3,
          title: 'Kiểm tra & Củng cố (Mini Quiz)',
          quiz: {
            question: 'Khi ReAct Agent nhận câu hỏi nằm ngoài phạm vi tài liệu đã tra cứu (Lớp chỗ khó ① - Nguồn sự thật), hành vi chuẩn theo HAX G10 là gì?',
            options: [
              'Tự suy đoán và trả lời câu hỏi dựa trên tri thức có sẵn của LLM mà không báo người dùng.',
              'Thông báo rõ ràng cho người dùng rằng không tìm thấy thông tin trong nguồn tra cứu và từ chối đoán (HAX G10).',
              'Lặp lại vòng lặp gọi tool vô tận đến khi tìm ra kết quả.'
            ],
            correct: 1,
            explanation: 'Chính xác! Theo HAX G10 (Thu hẹp phạm vi khi nghi ngờ), khi thông tin không có căn cứ xác thực, Agent phải từ chối đoán để bảo vệ niềm tin của người dùng.'
          }
        }
      ]
    },
    {
      id: 'lab-hax-02',
      title: 'Mini Lab 02: HAX Rules & Prompt Guardrails',
      morningTopic: 'Buổi 2 - Mức độ Tự động hoá & Ràng buộc HAX',
      morningSlideRef: 'Slide 02: HAX Guidelines [T02-045]',
      afternoonLabTarget: 'github.com/vlearn/day2-career-advisor-lab (4 tiếng)',
      duration: '15 phút',
      status: 'Mới',
      description: 'Thiết kế prompt có ràng buộc HAX G1 & G10 để tránh LLM hallucinate khi tư vấn.',
      steps: [
        {
          num: 1,
          title: 'Hiểu Lý thuyết & Cầu nối',
          content: `
            <div class="theory-bridge-box">
              <div class="theory-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 14l9-5-9-5-9 5 9 5z"/><path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0112 20.055a11.952 11.952 0 01-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/></svg>
                Trích dẫn Lý thuyết Sáng (Slide 02 - HAX Rules [T02-045])
              </div>
              <div class="theory-content">
                Thiết kế sản phẩm AI đòi hỏi chọn đúng mức độ tự động hoá: <strong>Augment (Gợi ý) vs Conditional (Tự động có điều kiện)</strong>.
                <br><br>
                Bài mini lab này giúp bạn gõ prompt cài đặt Guardrail cho OpenAI API trước khi nộp sản phẩm chiều.
              </div>
            </div>
          `
        },
        {
          num: 2,
          title: 'Thử nghiệm Code & Guardrail Prompt',
          starterCode: `# Cấu hình Guardrail Prompt cho OpenAI API
system_prompt = """
Bạn là Trợ lý VLearn. Bạn CHỈ được trả lời các câu hỏi nằm trong phạm vi khóa học AI.
Nếu người dùng hỏi chủ đề ngoài khóa học (ví dụ: tư vấn tài chính, y tế):
1. Nói rõ: "Xin lỗi, câu hỏi này nằm ngoài phạm vi hỗ trợ của Trợ lý VLearn." (HAX G1 & G10)
2. Gợi ý 1 chủ đề liên quan đến bài học AI mà bạn có thể hỗ trợ.
"""

def test_guardrail(user_input):
    print(f"User Question: '{user_input}'")
    if "chứng khoán" in user_input or "đầu tư" in user_input:
        return "[SYSTEM GUARDRAIL TRIGGERED] Xin lỗi, câu hỏi này nằm ngoài phạm vi hỗ trợ của Trợ lý VLearn (HAX G10)."
    return "[SYSTEM OK] Đang xử lý câu hỏi bài học AI..."

print(test_guardrail("Tôi có nên đầu tư chứng khoán năm nay không?"))
`
        },
        {
          num: 3,
          title: 'Kiểm tra & Củng cố (Mini Quiz)',
          quiz: {
            question: 'Tại sao cần đặt Guardrail HAX G1 & G10 ngay trong System Prompt?',
            options: [
              'Để giúp LLM trả lời câu hỏi nhanh hơn 50%.',
              'Để định hình kỳ vọng chuẩn cho user (G1) và từ chối an toàn khi vượt phạm vi (G10).',
              'Để tránh phải sử dụng OpenAI API.'
            ],
            correct: 1,
            explanation: 'Đúng rồi! Cài đặt Guardrail giúp sản phẩm không bị hallucinate và đảm bảo an toàn trải nghiệm.'
          }
        }
      ]
    }
  ]
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  renderApp();
});

// Render Main App Structure
function renderApp() {
  const root = document.getElementById('app');
  root.innerHTML = `
    <!-- Top Role Switching Bar -->
    <div class="role-bar">
      <div class="role-info">
        <span>K4 HACKATHON • CP2 PROTOTYPE</span>
        <span class="role-badge" id="role-display-text">Giao diện: 👨‍🎓 Học viên</span>
      </div>
      <div class="role-switcher">
        <button class="role-btn ${state.currentRole === 'student' ? 'active' : ''}" onclick="switchRole('student')">
          👨‍🎓 Học viên
        </button>
        <button class="role-btn ${state.currentRole === 'coach' ? 'active' : ''}" onclick="switchRole('coach')">
          👨‍🏫 Lab Coach Studio
        </button>
      </div>
    </div>

    <!-- VLearn Main Header -->
    <header class="vlearn-header">
      <div class="header-left">
        <a href="#" class="brand-logo" onclick="event.preventDefault()">
          <svg class="brand-icon" viewBox="0 0 32 32" fill="none">
            <path d="M6 8L16 26L26 8" stroke="#C8102E" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 8L16 16L20 8" stroke="#0C2340" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>VLearn</span>
        </a>
        <nav class="nav-links">
          <a class="nav-item active" onclick="event.preventDefault()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            Trang chủ
          </a>
          <a class="nav-item" onclick="event.preventDefault()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>
            Khóa học của tôi
          </a>
        </nav>
      </div>

      <div class="header-right">
        <button class="btn-codelabs-link" onclick="scrollToCodelabs()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          Mở Codelabs
        </button>
        <span class="lang-badge">VI</span>
        <button class="theme-toggle-btn" onclick="toggleTheme()" title="Đổi giao diện">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
        </button>
        <div class="user-profile-badge">
          <div class="user-avatar-num">2</div>
          <span class="user-email">hocvien.ai@vlearn.edu.vn</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
      </div>
    </header>

    <!-- Main Page Content -->
    <main class="page-container">
      ${state.currentRole === 'student' ? renderStudentDashboard() : renderCoachStudio()}
    </main>

    <!-- Modal Workspace Container -->
    <div id="modal-container"></div>

    <footer class="vlearn-footer">
      <p>© 2026 VLearn - Nền tảng học tập VinUni AI Thực Chiến • Giải pháp AI Sinh Mini Codelab (CP2 Prototype)</p>
    </footer>
  `;
}

// Switch Role
window.switchRole = function(role) {
  state.currentRole = role;
  renderApp();
};

// Toggle Dark/Light Theme
window.toggleTheme = function() {
  state.theme = state.theme === 'light' ? 'dark' : 'light';
  if (state.theme === 'dark') {
    document.body.classList.add('dark-mode');
  } else {
    document.body.classList.remove('dark-mode');
  }
};

// Scroll Smooth to Codelabs
window.scrollToCodelabs = function() {
  const el = document.getElementById('codelabs-section');
  if (el) el.scrollIntoView({ behavior: 'smooth' });
};

// Render Student View (Matching Image Layout)
function renderStudentDashboard() {
  return `
    <!-- Top Section Header -->
    <div class="section-header">
      <div>
        <div class="breadcrumb-tag">VLEARN • VINUNI AI THỰC CHIẾN</div>
        <h1 class="page-title">Không gian học tập VLearn</h1>
        <p class="page-subtitle">Theo dõi tiến độ, học liệu và phần kiến thức cần củng cố tại VinUni AI Thực Chiến.</p>
      </div>
      <div class="course-count-badge">
        1 khóa học đang theo học
      </div>
    </div>

    <!-- Welcome Banner Card (Exact Replica of Image) -->
    <div class="welcome-banner">
      <div class="welcome-banner-bg-shape"></div>
      <div class="welcome-banner-content">
        <div class="banner-sublabel">VLEARN • VINUNI AI THỰC CHIẾN</div>
        <h2 class="banner-title">Chào mừng trở lại, HỌC VIÊN VLEARN!</h2>
        <p class="banner-desc">
          VLearn đang tổng hợp tiến độ đọc và các tín hiệu học tập. Mở Khóa học của tôi để tiếp tục ngày học hoặc trao đổi cùng VLearn Tutor.
        </p>
        <div class="banner-tags">
          <span class="status-pill active">
            <span class="dot"></span> Tín hiệu học tập đang hoạt động
          </span>
          <span class="status-pill read-status">
            Đã đọc 0/6 ngày học
          </span>
        </div>
      </div>
    </div>

    <!-- Statistics Grid (Exact Replica of Image) -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon-box">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>
        </div>
        <div>
          <div class="stat-label">KHÓA HỌC</div>
          <div class="stat-value">1</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-box">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        </div>
        <div>
          <div class="stat-label">CÂU HỎI VỚI TUTOR</div>
          <div class="stat-value">6</div>
        </div>
      </div>
    </div>

    <!-- Wide Action Card (Exact Replica of Image) -->
    <div class="course-action-card" onclick="scrollToCodelabs()">
      <div class="action-card-left">
        <div class="action-card-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>
        </div>
        <div>
          <div class="action-card-title">Xem khóa học của tôi</div>
          <div class="action-card-desc">Mở danh sách đầy đủ các lớp bạn đang theo học và danh sách Mini Codelab buổi sáng.</div>
        </div>
      </div>
      <div class="action-card-arrow">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
      </div>
    </div>

    <!-- CP2 CORE FEATURE: Mini Codelab Buổi Sáng -->
    <div id="codelabs-section">
      <div class="codelab-section-title">
        <h2>
          <span>⚡ Mini Codelab Buổi Sáng (AI Agent Generated)</span>
          <span class="codelab-section-badge">Cầu nối bài Lab Chiều</span>
        </h2>
        <span class="tag-duration">Giúp thông tư tưởng lý thuyết trước giờ Lab 4 tiếng</span>
      </div>

      <div class="codelabs-grid">
        ${state.codelabs.map(lab => `
          <div class="codelab-item-card">
            <div>
              <div class="codelab-card-tag">
                <span class="tag-morning">${lab.morningTopic}</span>
                <span class="tag-duration">⏱️ ${lab.duration}</span>
              </div>
              <h3 class="codelab-card-h3">${lab.title}</h3>
              <p class="codelab-card-desc">${lab.description}</p>
              <div class="codelab-card-meta">
                <strong>🔗 Trích dẫn Slide:</strong> ${lab.morningSlideRef}<br>
                <strong>🎯 Chuẩn bị cho Lab chiều:</strong> ${lab.afternoonLabTarget}
              </div>
            </div>
            <button class="btn-primary" onclick="openCodelabWorkspace('${lab.id}')">
              <span>🚀 Bắt đầu làm Mini Lab</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            </button>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// Render Lab Coach Studio View
function renderCoachStudio() {
  return `
    <div class="section-header">
      <div>
        <div class="breadcrumb-tag">LAB COACH STUDIO • AI AGENT GENERATOR</div>
        <h1 class="page-title">Tạo Mini Codelab bằng AI Agent</h1>
        <p class="page-subtitle">Nhập slide bài giảng sáng + repo lab chiều để AI Agent tự tổng hợp Mini Codelab 15 phút cho học viên.</p>
      </div>
    </div>

    <div class="coach-studio-card">
      <form onsubmit="event.preventDefault(); handleCoachGenerate();">
        <div class="form-group">
          <label class="form-label">1. Slide / Chủ đề Bài giảng Buổi sáng</label>
          <select id="coach-morning-slide" class="form-control">
            <option value="d1-slide-hackathon.pdf - Day 4: ReAct Agent Architecture & Tool Calling">d1-slide-hackathon.pdf - Day 4: ReAct Agent Architecture & Tool Calling</option>
            <option value="d1-slide-hackathon.pdf - Day 2: HAX Rules & Conditional Automation">d1-slide-hackathon.pdf - Day 2: HAX Rules & Conditional Automation</option>
            <option value="d2-slide-hackathon.pdf - Day 5: Eval Golden Set & Red Teaming">d2-slide-hackathon.pdf - Day 5: Eval Golden Set & Red Teaming</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">2. Repo / Đề bài Codelab Buổi chiều (4 tiếng)</label>
          <input type="text" id="coach-afternoon-repo" class="form-control" value="github.com/vlearn/day4-research-agent-lab" placeholder="Link GitHub repo hoặc mô tả bài lab chiều...">
        </div>

        <div class="form-group">
          <label class="form-label">3. Ràng buộc & Cấu hình Code Agent (Constraint Policy)</label>
          <div class="checkbox-group mb-3">
            <label class="checkbox-label"><input type="checkbox" checked disabled> <code>openai</code> API</label>
            <label class="checkbox-label"><input type="checkbox" checked> <code>pydantic</code></label>
            <label class="checkbox-label"><input type="checkbox" checked> <code>python-dotenv</code></label>
            <label class="checkbox-label"><input type="checkbox"> <code>fastapi</code></label>
          </div>
          <textarea id="coach-prompt-rules" class="form-control" rows="3" placeholder="Ràng buộc prompt...">Chỉ sinh code Python đơn giản dưới 50 dòng, có comment giải thích vòng lặp ReAct, đính kèm 1 câu hỏi kiểm tra HAX G10.</textarea>
        </div>

        <div class="form-group">
          <label class="form-label">4. Cấu hình OpenAI API (Tùy chọn cho Live Agent Call)</label>
          <input type="password" id="coach-api-key" class="form-control" placeholder="sk-proj-... (Để trống sẽ sử dụng AI Agent Generator có sẵn)">
        </div>

        <button type="submit" class="btn-primary" style="font-size: 15px; padding: 12px 24px;">
          <span>✨ Sinh Mini Codelab bằng AI Agent</span>
        </button>
      </form>

      <!-- Live Generation Stepper Container -->
      <div id="coach-generation-progress" style="display: none;"></div>
    </div>
  `;
}

// Open Codelab Workspace Modal
window.openCodelabWorkspace = function(labId) {
  const lab = state.codelabs.find(c => c.id === labId);
  if (!lab) return;

  state.activeCodelabId = labId;
  state.activeStep = 1;

  renderWorkspaceModal(lab);
};

// Close Modal
window.closeModal = function() {
  document.getElementById('modal-container').innerHTML = '';
};

// Switch Modal Step Tab
window.switchModalStep = function(stepNum) {
  state.activeStep = stepNum;
  const lab = state.codelabs.find(c => c.id === state.activeCodelabId);
  if (lab) renderWorkspaceModal(lab);
};

// Render Workspace Modal
function renderWorkspaceModal(lab) {
  const currentStep = lab.steps.find(s => s.num === state.activeStep);

  const container = document.getElementById('modal-container');
  container.innerHTML = `
    <div class="modal-overlay" onclick="if(event.target === this) closeModal()">
      <div class="workspace-modal">
        <div class="workspace-header">
          <div class="workspace-title-box">
            <h3>${lab.title}</h3>
            <span class="workspace-subtitle">⏱️ Thời lượng: ${lab.duration} • ${lab.morningSlideRef}</span>
          </div>
          <button class="modal-close-btn" onclick="closeModal()">✕</button>
        </div>

        <!-- Stepper Navigation -->
        <div class="workspace-stepper">
          ${lab.steps.map(s => `
            <div class="step-tab ${s.num === state.activeStep ? 'active' : ''}" onclick="switchModalStep(${s.num})">
              <span>Step ${s.num}: ${s.title}</span>
            </div>
          `).join('')}
        </div>

        <div class="workspace-body">
          ${renderStepContent(lab, currentStep)}
        </div>
      </div>
    </div>
  `;
}

// Render Step Content
function renderStepContent(lab, step) {
  if (step.num === 1) {
    return `
      ${step.content}
      <div style="text-align: right; margin-top: 20px;">
        <button class="btn-primary" style="width: auto; display: inline-flex;" onclick="switchModalStep(2)">
          <span>Tiếp tục: Thử nghiệm Code Step 2</span> ➔
        </button>
      </div>
    `;
  }

  if (step.num === 2) {
    return `
      <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">
        Gõ và chạy đoạn code Python ReAct Agent dưới đây để xem log tương tác thực tế:
      </p>

      <div class="playground-container">
        <div class="code-editor-box">
          <div class="box-header">
            <span>🐍 Python Mini ReAct Sandbox</span>
            <button class="btn-secondary" style="padding: 2px 8px; font-size: 11px;" onclick="resetCode('${lab.id}')">Reset Code</button>
          </div>
          <textarea id="code-input" class="code-textarea">${step.starterCode}</textarea>
        </div>

        <div class="output-box">
          <div class="box-header">
            <span>🖥️ Terminal Output & ReAct Logs</span>
            <span style="color: #34d399; font-size: 11px;">● Ready</span>
          </div>
          <div id="console-output" class="console-output">
Click [ ▶ Chạy Mini Agent ] để xem vòng lặp ReAct hoạt động...
          </div>
        </div>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center;">
        <button class="btn-secondary" style="width: auto;" onclick="switchModalStep(1)">
          ⬅ Step 1
        </button>
        <button class="btn-primary" style="width: auto; display: inline-flex;" onclick="runMiniAgentCode()">
          <span>▶ Chạy Mini Agent</span>
        </button>
      </div>
    `;
  }

  if (step.num === 3) {
    const q = step.quiz;
    return `
      <div style="max-width: 700px; margin: 0 auto; background: var(--bg-page); padding: 24px; border-radius: var(--border-radius-md); border: 1px solid var(--border-color);">
        <h4 style="font-size: 16px; margin-bottom: 14px; color: var(--navy-dark);">❓ Câu hỏi củng cố (Mini Quiz):</h4>
        <p style="font-size: 14px; font-weight: 600; margin-bottom: 16px;">${q.question}</p>

        <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px;">
          ${q.options.map((opt, idx) => `
            <button class="btn-secondary" style="text-align: left; justify-content: flex-start; padding: 12px 16px;" onclick="handleQuizAnswer(${idx}, ${q.correct}, '${encodeURIComponent(q.explanation)}')">
              ${String.fromCharCode(65 + idx)}. ${opt}
            </button>
          `).join('')}
        </div>

        <div id="quiz-result-box"></div>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 24px;">
        <button class="btn-secondary" style="width: auto;" onclick="switchModalStep(2)">
          ⬅ Step 2
        </button>
        <button class="btn-primary" style="width: auto;" onclick="closeModal()">
          🎉 Hoàn thành Mini Lab!
        </button>
      </div>
    `;
  }
}

// Run Interactive Code Execution Simulation
window.runMiniAgentCode = function() {
  const outputEl = document.getElementById('console-output');
  outputEl.innerHTML = `<span style="color: #facc15;">⏳ Đang khởi chạy ReAct Agent Engine...</span>\n`;

  setTimeout(() => {
    outputEl.innerHTML = `
<span class="console-log-thought">[THOUGHT 1]</span> Người dùng yêu cầu bài báo về 'ReAct Agent'.
<span class="console-log-action">[ACTION 1]</span> Invoking tool: lookup_paper(query='react')
<span class="console-log-observation">[OBSERVATION 1]</span> Query success: "ReAct: Synergizing Reasoning and Acting in LLMs (Yao et al., 2022)"
<span class="console-log-thought">[THOUGHT 2]</span> Đã tìm thấy kết quả chính xác từ database.
<span class="console-log-final">[FINAL ANSWER]</span> 
--------------------------------------------------
Bài báo theo yêu cầu của bạn là:
"ReAct: Synergizing Reasoning and Acting in LLMs"
Tác giả: Yao et al., 2022
--------------------------------------------------
<span style="color: #34d399;">✔ ReAct Loop completed in 0.42s (Cost-of-error: Low)</span>
`;
  }, 600);
};

// Handle Quiz Answer
window.handleQuizAnswer = function(selectedIdx, correctIdx, explanationEscaped) {
  const explanation = decodeURIComponent(explanationEscaped);
  const resultBox = document.getElementById('quiz-result-box');

  if (selectedIdx === correctIdx) {
    resultBox.innerHTML = `
      <div style="background: #dcfce7; color: #166534; padding: 14px; border-radius: 8px; border: 1px solid #86efac; font-size: 13px;">
        <strong>🎉 ĐÚNG RỒI!</strong><br>${explanation}
      </div>
    `;
  } else {
    resultBox.innerHTML = `
      <div style="background: #fee2e2; color: #991b1b; padding: 14px; border-radius: 8px; border: 1px solid #fca5a5; font-size: 13px;">
        <strong>❌ CHƯA CHÍNH XÁC.</strong><br>Hãy thử lại lựa chọn đúng theo HAX G10 nhé!
      </div>
    `;
  }
};

// Handle Coach AI Generator
window.handleCoachGenerate = function() {
  const morningSlide = document.getElementById('coach-morning-slide').value;
  const afternoonRepo = document.getElementById('coach-afternoon-repo').value;
  const rules = document.getElementById('coach-prompt-rules').value;

  const progressBox = document.getElementById('coach-generation-progress');
  progressBox.style.display = 'block';
  progressBox.innerHTML = `
    <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 12px; color: var(--navy-dark);">
      🤖 AI Agent đang tổng hợp Mini Codelab...
    </h4>
    <div class="progress-step-item active" id="pstep-1">
      <div class="progress-step-icon">1</div>
      <span>Phân tích slide bài giảng sáng: "${morningSlide}"...</span>
    </div>
    <div class="progress-step-item" id="pstep-2">
      <div class="progress-step-icon">2</div>
      <span>Đọc hiểu yêu cầu repo lab chiều: "${afternoonRepo}"...</span>
    </div>
    <div class="progress-step-item" id="pstep-3">
      <div class="progress-step-icon">3</div>
      <span>Tổng hợp 3 mini steps & ràng buộc code...</span>
    </div>
  `;

  setTimeout(() => {
    document.getElementById('pstep-1').className = 'progress-step-item done';
    document.getElementById('pstep-2').className = 'progress-step-item active';
  }, 1000);

  setTimeout(() => {
    document.getElementById('pstep-2').className = 'progress-step-item done';
    document.getElementById('pstep-3').className = 'progress-step-item active';
  }, 2000);

  setTimeout(() => {
    document.getElementById('pstep-3').className = 'progress-step-item done';

    // Add generated Mini Codelab to state
    const newLabId = `lab-gen-${Date.now()}`;
    const newLab = {
      id: newLabId,
      title: `Mini Lab: AI Agent Generated cho ${afternoonRepo.split('/').pop()}`,
      morningTopic: morningSlide.split(' - ')[1] || 'Slide Buổi Sáng',
      morningSlideRef: morningSlide,
      afternoonLabTarget: afternoonRepo,
      duration: '15 phút',
      status: 'Vừa sinh',
      description: `Mini lab 15 phút do AI Agent vừa tự động khởi tạo từ slide sáng và repo chiều với ràng buộc: "${rules.substring(0, 60)}..."`,
      steps: [
        {
          num: 1,
          title: 'Hiểu Lý thuyết & Cầu nối',
          content: `
            <div class="theory-bridge-box">
              <div class="theory-title">Trích dẫn AI Generator Bridge</div>
              <div class="theory-content">
                Bài mini lab này được AI Agent sinh tự động nhằm nối liền lý thuyết <strong>${morningSlide}</strong> với dự án 4 tiếng buổi chiều tại <strong>${afternoonRepo}</strong>.
              </div>
            </div>
          `
        },
        {
          num: 2,
          title: 'Thử nghiệm Code Generated',
          starterCode: `# AI Agent Generated Code Mini Lab
import openai

def generated_agent_step():
    print("[AI GENERATED MINI STEP] Safe call setup completed.")
    return "Mini step executed smoothly!"

print(generated_agent_step())
`
        },
        {
          num: 3,
          title: 'Kiểm tra & Củng cố (Mini Quiz)',
          quiz: {
            question: 'Mục đích của việc học Mini Codelab 15 phút buổi sáng là gì?',
            options: [
              'Để thay thế hoàn toàn bài lab 4 tiếng buổi chiều.',
              'Để thông tư tưởng lý thuyết và hiểu bản chất code trước khi vào bài lab 4 tiếng.',
              'Để nộp bài chấm điểm trực tiếp.'
            ],
            correct: 1,
            explanation: 'Đúng rồi! Mini lab giúp học viên tự tin thông qua bài lab 4 tiếng buổi chiều mà không bị phụ thuộc lạm dụng AI.'
          }
        }
      ]
    };

    state.codelabs.unshift(newLab);

    progressBox.innerHTML += `
      <div style="margin-top: 16px; padding: 14px; background: #dcfce7; border-radius: 8px; color: #166534; font-size: 13px;">
        <strong>✔ ĐÃ TẠO THÀNH CÔNG MINI CODELAB!</strong><br>
        Mini Codelab đã được phát hành lên không gian học tập của Học viên.
        <br><br>
        <button class="btn-primary" style="width: auto;" onclick="switchRole('student')">
          👉 Chuyển sang Giao diện Học viên để xem ngay
        </button>
      </div>
    `;
  }, 3200);
};
