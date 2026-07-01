// ===== App State =====
const state = {
  user: null,
  token: localStorage.getItem('access_token') || null,
  strategies: [],
  currentStrategy: null,
  backtestResults: [],
  currentBacktestDetail: null,
  chatHistory: [],
  loading: false,
  editor: null,
  charts: {}
};

// ===== API Helper =====
const BASE = 'http://localhost:8000/api';

async function api(method, path, body = null) {
  const headers = { 'Content-Type': 'application/json' };
  if (state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }
  const config = { method, headers };
  if (body) config.body = JSON.stringify(body);
  const res = await fetch(`${BASE}${path}`, config);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || 'Request failed');
  }
  const contentType = res.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await res.json();
  }
  return null;
}

// ===== Routing =====
function navigate(hash) {
  window.location.hash = hash;
}

function getRoute() {
  const hash = window.location.hash.slice(1) || '/login';
  return hash;
}

function router() {
  const route = getRoute();
  const mainEl = document.getElementById('app');
  if (!mainEl) return;
  if (!state.token && !['/login','/register'].includes(route)) {
    navigate('/login');
    return;
  }
  switch (true) {
    case route === '/login':
      renderLogin();
      break;
    case route === '/register':
      renderRegister();
      break;
    case route === '/' || route === '/home':
      renderHome();
      break;
    case route.startsWith('/strategy/edit/'):
      const id = route.split('/')[3];
      renderEditPage(id);
      break;
    case route === '/strategies':
      renderStrategies();
      break;
    case route === '/backtest-results':
      renderBacktestResults();
      break;
    case route.startsWith('/strategy/performance/'):
      const btId = route.split('/')[3];
      renderPerformance(btId);
      break;
    default:
      navigate('/');
  }
}

window.addEventListener('hashchange', router);
window.addEventListener('load', router);

// ===== Layout =====
function renderLayout(contentHtml) {
  const app = document.getElementById('app');
  if (['/login','/register'].includes(getRoute())) {
    app.innerHTML = contentHtml;
    return;
  }
  app.innerHTML = `
    <div class="sidebar">
      <div class="logo">AI策略系统</div>
      <a class="nav-item ${getRoute() === '/' || getRoute() === '/home' ? 'active' : ''}" onclick="navigate('/')"><i>🏠</i><span>首页</span></a>
      <a class="nav-item ${getRoute() === '/strategies' ? 'active' : ''}" onclick="navigate('/strategies')"><i>📋</i><span>策略列表</span></a>
      <a class="nav-item ${getRoute() === '/backtest-results' ? 'active' : ''}" onclick="navigate('/backtest-results')"><i>📊</i><span>回测结果</span></a>
    </div>
    <div class="main">
      <div class="topbar">
        <div></div>
        <div class="user-info">
          <span class="username">${state.user ? state.user.username : ''}</span>
          <button class="logout-btn" onclick="handleLogout()">退出</button>
        </div>
      </div>
      <div class="content">${contentHtml}</div>
    </div>
  `;
  // Attach sidebar click handlers
  document.querySelectorAll('.sidebar .nav-item').forEach(el => {
    el.addEventListener('click', function(e) {
      e.preventDefault();
      navigate(this.getAttribute('onclick').match(/'([^']+)'/)[1]);
    });
  });
}

// ===== Auth Pages =====
function renderLogin() {
  document.getElementById('app').innerHTML = `
    <div class="auth-page">
      <div class="auth-card">
        <h2>登录</h2>
        <form id="loginForm">
          <div class="form-group">
            <label for="username">用户名</label>
            <input class="form-control" id="loginUsername" placeholder="请输入用户名" required minlength="3">
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input type="password" class="form-control" id="loginPassword" placeholder="请输入密码" required minlength="6">
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;">登录</button>
        </form>
        <div class="auth-link">
          没有账号？ <a onclick="navigate('/register')">立即注册</a>
        </div>
        <div id="loginError" style="color:red;margin-top:8px;text-align:center;"></div>
      </div>
    </div>
  `;
  document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    try {
      const data = await api('POST', '/auth/login', { username, password });
      state.token = data.access_token;
      localStorage.setItem('access_token', data.access_token);
      // Fetch user info (we'll just store username)
      state.user = { username };
      navigate('/');
    } catch (err) {
      document.getElementById('loginError').textContent = err.message;
    }
  });
}

function renderRegister() {
  document.getElementById('app').innerHTML = `
    <div class="auth-page">
      <div class="auth-card">
        <h2>注册</h2>
        <form id="registerForm">
          <div class="form-group">
            <label for="regUsername">用户名</label>
            <input class="form-control" id="regUsername" placeholder="至少3个字符" required minlength="3">
          </div>
          <div class="form-group">
            <label for="regPassword">密码</label>
            <input type="password" class="form-control" id="regPassword" placeholder="至少6个字符" required minlength="6">
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;">注册</button>
        </form>
        <div class="auth-link">
          已有账号？ <a onclick="navigate('/login')">立即登录</a>
        </div>
        <div id="regError" style="color:red;margin-top:8px;text-align:center;"></div>
      </div>
    </div>
  `;
  document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;
    try {
      const data = await api('POST', '/auth/register', { username, password });
      // Auto-login after register
      const loginData = await api('POST', '/auth/login', { username, password });
      state.token = loginData.access_token;
      localStorage.setItem('access_token', loginData.access_token);
      state.user = { username };
      navigate('/');
    } catch (err) {
      document.getElementById('regError').textContent = err.message;
    }
  });
}

function handleLogout() {
  state.token = null;
  state.user = null;
  localStorage.removeItem('access_token');
  navigate('/login');
}

// ===== Home Page =====
function renderHome() {
  renderLayout(`
    <div class="home-container">
      <div class="home-title">AI 策略生成</div>
      <div class="home-subtitle">描述你的策略需求，AI将为你生成聚宽标准策略代码</div>
      <div class="home-input-wrapper">
        <textarea id="promptInput" placeholder="例如：生成一个双均线策略"></textarea>
        <button class="btn btn-primary send-btn" id="generateBtn">发送</button>
      </div>
      <div id="codePreview" style="display:none;margin-top:16px;width:100%;max-width:800px;">
        <div class="card">
          <h4>生成的策略代码</h4>
          <pre id="generatedCode" style="background:#282c34;color:#abb2bf;padding:12px;border-radius:4px;overflow:auto;max-height:300px;"></pre>
          <p style="margin-top:8px;color:var(--text-secondary);">正在跳转到策略编辑页...</p>
        </div>
      </div>
      <div id="homeError" style="color:red;margin-top:8px;"></div>
    </div>
  `);
  document.getElementById('generateBtn').addEventListener('click', handleGenerate);
  document.getElementById('promptInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  });
}

async function handleGenerate() {
  const prompt = document.getElementById('promptInput').value.trim();
  if (!prompt) {
    document.getElementById('homeError').textContent = '请输入策略需求';
    return;
  }
  const btn = document.getElementById('generateBtn');
  btn.disabled = true;
  btn.textContent = '生成中...';
  try {
    const data = await api('POST', '/chat/generate', { prompt });
    document.getElementById('codePreview').style.display = 'block';
    document.getElementById('generatedCode').textContent = data.code;
    // After 2 seconds, navigate to edit page
    setTimeout(() => {
      navigate(`/strategy/edit/${data.strategy_id}`);
    }, 2000);
  } catch (err) {
    document.getElementById('homeError').textContent = err.message;
  } finally {
    btn.disabled = false;
    btn.textContent = '发送';
  }
}

// ===== Edit Page =====
function renderEditPage(strategyId) {
  renderLayout(`
    <div class="editor-panel">
      <div class="editor-left">
        <div class="editor-actions">
          <button class="btn btn-primary" id="saveStrategyBtn">💾 保存</button>
          <button class="btn btn-success" id="quickBacktestBtn">⚡ 快速回测</button>
          <button class="btn btn-warning" id="analysisBtn">📈 运行回测绩效分析</button>
        </div>
        <div id="editorContainer"></div>
      </div>
      <div class="editor-right">
        <div class="tabs">
          <div class="tab active" data-tab="chat">多轮对话</div>
          <div class="tab" data-tab="backtest">快速回测结果</div>
        </div>
        <div class="tab-content" id="tabContent">
          <!-- Chat tab -->
          <div id="chatPanel" style="display:flex;flex-direction:column;height:100%;">
            <div id="chatMessages" class="chat-messages"></div>
            <div class="chat-input-area">
              <input class="form-control" id="chatInput" placeholder="输入修改指令...">
              <button class="btn btn-primary" id="chatSendBtn">发送</button>
            </div>
          </div>
          <!-- Backtest tab -->
          <div id="backtestTab" style="display:none;overflow-y:auto;">
            <div id="quickResultMetrics" class="metric-row"></div>
            <div id="quickChartContainer" class="chart-container" style="height:300px;">
              <h3>净值曲线</h3>
              <canvas id="quickNetValueChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  `);
  // Load strategy
  loadStrategy(strategyId);
  // Tab switching
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      const tabName = this.dataset.tab;
      document.getElementById('chatPanel').style.display = tabName === 'chat' ? 'flex' : 'none';
      document.getElementById('backtestTab').style.display = tabName === 'backtest' ? 'block' : 'none';
    });
  });
  // Event handlers
  document.getElementById('saveStrategyBtn').addEventListener('click', handleSaveStrategy);
  document.getElementById('quickBacktestBtn').addEventListener('click', handleQuickBacktest);
  document.getElementById('analysisBtn').addEventListener('click', handleAnalysis);
  document.getElementById('chatSendBtn').addEventListener('click', handleChatSend);
  document.getElementById('chatInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleChatSend();
    }
  });
}

async function loadStrategy(id) {
  try {
    const data = await api('GET', `/strategies/${id}`);
    state.currentStrategy = data;
    initEditor(data.code);
    state.chatHistory = [];
    document.getElementById('chatMessages').innerHTML = '';
  } catch (err) {
    alert('加载策略失败: ' + err.message);
  }
}

function initEditor(code) {
  const container = document.getElementById('editorContainer');
  container.innerHTML = '';
  const textarea = document.createElement('textarea');
  textarea.id = 'codeEditor';
  textarea.value = code;
  container.appendChild(textarea);
  if (window.CodeMirror) {
    state.editor = CodeMirror.fromTextArea(textarea, {
      mode: 'python',
      theme: 'dracula',
      lineNumbers: true,
      autoRefresh: true,
      indentUnit: 4
    });
  }
}

function getEditorCode() {
  if (state.editor) {
    return state.editor.getValue();
  }
  return document.getElementById('codeEditor')?.value || '';
}

async function handleSaveStrategy() {
  const btn = document.getElementById('saveStrategyBtn');
  btn.disabled = true;
  btn.textContent = '保存中...';
  try {
    const code = getEditorCode();
    const payload = {
      id: state.currentStrategy.id,
      name: state.currentStrategy.name || '新策略',
      description: state.currentStrategy.description || '',
      code: code
    };
    const data = await api('POST', '/strategies', payload);
    alert('保存成功');
    state.currentStrategy.id = data.id;
  } catch (err) {
    alert('保存失败: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '💾 保存';
  }
}

async function handleQuickBacktest() {
  const btn = document.getElementById('quickBacktestBtn');
  btn.disabled = true;
  btn.textContent = '回测中...';
  try {
    const code = getEditorCode();
    const data = await api('POST', '/backtest/quick', { code, strategy_id: state.currentStrategy.id });
    // Switch to backtest tab
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-tab="backtest"]').classList.add('active');
    document.getElementById('chatPanel').style.display = 'none';
    document.getElementById('backtestTab').style.display = 'block';
    // Display metrics
    const result = data.result;
    const metricsHtml = `
      <div class="metric-card"><div class="metric-label">总收益率</div><div class="metric-value ${result.total_return_pct >= 0 ? 'positive' : 'negative'}">${result.total_return_pct}%</div></div>
      <div class="metric-card"><div class="metric-label">年化收益率</div><div class="metric-value ${result.annual_return_pct >= 0 ? 'positive' : 'negative'}">${result.annual_return_pct}%</div></div>
      <div class="metric-card"><div class="metric-label">最大回撤</div><div class="metric-value negative">${result.max_drawdown_pct}%</div></div>
      <div class="metric-card"><div class="metric-label">夏普比率</div><div class="metric-value positive">${result.sharpe_ratio}</div></div>
    `;
    document.getElementById('quickResultMetrics').innerHTML = metricsHtml;
    // Draw chart
    if (window.Chart && result.net_value_curve) {
      const ctx = document.getElementById('quickNetValueChart').getContext('2d');
      if (state.charts.quickNetValue) state.charts.quickNetValue.destroy();
      state.charts.quickNetValue = new Chart(ctx, {
        type: 'line',
        data: {
          labels: result.net_value_curve.map(p => p.date),
          datasets: [{
            label: '净值',
            data: result.net_value_curve.map(p => p.value),
            borderColor: '#1890ff',
            fill: false,
            tension: 0.1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
    }
  } catch (err) {
    alert('快速回测失败: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '⚡ 快速回测';
  }
}

async function handleAnalysis() {
  const btn = document.getElementById('analysisBtn');
  btn.disabled = true;
  btn.textContent = '分析中...';
  try {
    const code = getEditorCode();
    const data = await api('POST', '/backtest/analysis', { strategy_id: state.currentStrategy.id, code });
    navigate(`/strategy/performance/${data.backtest_id}`);
  } catch (err) {
    alert('运行回测绩效分析失败: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '📈 运行回测绩效分析';
  }
}

async function handleChatSend() {
  const input = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;
  // Add user message to chat
  const chatMessages = document.getElementById('chatMessages');
  chatMessages.innerHTML += `<div class="chat-message user">${message}</div>`;
  input.value = '';
  try {
    const data = await api('POST', '/chat/continue', {
      strategy_id: state.currentStrategy.id,
      message,
      history: state.chatHistory
    });
    // Update editor code
    if (state.editor) {
      state.editor.setValue(data.code);
    }
    // Add AI reply
    chatMessages.innerHTML += `<div class="chat-message ai">${data.reply}</div>`;
    state.chatHistory.push({ role: 'user', content: message });
    state.chatHistory.push({ role: 'assistant', content: data.reply });
    chatMessages.scrollTop = chatMessages.scrollHeight;
  } catch (err) {
    chatMessages.innerHTML += `<div class="chat-message ai" style="color:red;">错误: ${err.message}</div>`;
  }
}

// ===== Strategies Page =====
function renderStrategies() {
  renderLayout(`
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <h2>我的策略</h2>
      <button class="btn btn-primary" onclick="navigate('/')">+ 新建策略</button>
    </div>
    <div id="strategiesTableContainer">
      <p>加载中...</p>
    </div>
  `);
  loadStrategiesTable();
}

async function loadStrategiesTable() {
  try {
    const data = await api('GET', '/strategies');
    state.strategies = data.strategies;
    const container = document.getElementById('strategiesTableContainer');
    if (state.strategies.length === 0) {
      container.innerHTML = '<div class="card text-center">暂无策略，点击上方新建按钮创建。</div>';
      return;
    }
    let html = '<table><thead><tr><th>名称</th><th>描述</th><th>创建时间</th><th>操作</th></tr></thead><tbody>';
    state.strategies.forEach(s => {
      html += `<tr>
        <td>${s.name}</td>
        <td>${s.description || '-'}</td>
        <td>${new Date(s.created_at).toLocaleString()}</td>
        <td>
          <button class="btn btn-outline btn-sm" onclick="navigate('/strategy/edit/${s.id}')">编辑</button>
          <button class="btn btn-danger btn-sm" onclick="handleDeleteStrategy(${s.id})">删除</button>
        </td>
      </tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
  } catch (err) {
    document.getElementById('strategiesTableContainer').innerHTML = `<div style="color:red;">加载失败: ${err.message}</div>`;
  }
}

async function handleDeleteStrategy(id) {
  if (!confirm('确定要删除该策略吗？')) return;
  try {
    await api('DELETE', `/strategies/${id}`);
    loadStrategiesTable();
  } catch (err) {
    alert('删除失败: ' + err.message);
  }
}

// ===== Backtest Results Page =====
function renderBacktestResults() {
  renderLayout(`
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <h2>回测结果</h2>
      <select id="typeFilter" class="form-control" style="width:200px;">
        <option value="">全部</option>
        <option value="quick">快速回测</option>
        <option value="full">绩效分析</option>
      </select>
    </div>
    <div id="backtestTableContainer">
      <p>加载中...</p>
    </div>
  `);
  loadBacktestResults('');
  document.getElementById('typeFilter').addEventListener('change', function() {
    loadBacktestResults(this.value);
  });
}

async function loadBacktestResults(type) {
  try {
    const url = type ? `/backtest-results?type=${type}` : '/backtest-results';
    const data = await api('GET', url);
    state.backtestResults = data.results;
    const container = document.getElementById('backtestTableContainer');
    if (state.backtestResults.length === 0) {
      container.innerHTML = '<div class="card text-center">暂无回测结果。</div>';
      return;
    }
    let html = '<table><thead><tr><th>类型</th><th>关联策略ID</th><th>创建时间</th><th>操作</th></tr></thead><tbody>';
    state.backtestResults.forEach(r => {
      const typeLabel = r.type === 'quick' ? '<span class="tag tag-quick">快速</span>' : '<span class="tag tag-full">绩效分析</span>';
      html += `<tr>
        <td>${typeLabel}</td>
        <td>${r.strategy_id || '-'}</td>
        <td>${new Date(r.created_at).toLocaleString()}</td>
        <td>
          ${r.type === 'full' ? `<button class="btn btn-outline btn-sm" onclick="navigate('/strategy/performance/${r.id}')">查看详情</button>` : `<button class="btn btn-outline btn-sm" onclick="showQuickDetail(${r.id})">查看详情</button>`}
        </td>
      </tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
  } catch (err) {
    document.getElementById('backtestTableContainer').innerHTML = `<div style="color:red;">加载失败: ${err.message}</div>`;
  }
}

function showQuickDetail(id) {
  const result = state.backtestResults.find(r => r.id === id);
  if (!result) return;
  const data = result.result_data;
  const modalHtml = `
    <div class="modal-overlay" onclick="this.remove()">
      <div class="modal-content" onclick="event.stopPropagation()">
        <h3>快速回测详情</h3>
        <div class="metric-row">
          <div class="metric-card"><div class="metric-label">总收益率</div><div class="metric-value ${data.total_return_pct >= 0 ? 'positive' : 'negative'}">${data.total_return_pct}%</div></div>
          <div class="metric-card"><div class="metric-label">年化收益率</div><div class="metric-value ${data.annual_return_pct >= 0 ? 'positive' : 'negative'}">${data.annual_return_pct}%</div></div>
          <div class="metric-card"><div class="metric-label">最大回撤</div><div class="metric-value negative">${data.max_drawdown_pct}%</div></div>
          <div class="metric-card"><div class="metric-label">夏普比率</div><div class="metric-value positive">${data.sharpe_ratio}</div></div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove()">关闭</button>
        </div>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// ===== Performance Page =====
function renderPerformance(backtestId) {
  renderLayout(`
    <div style="margin-bottom:16px;">
      <button class="btn btn-outline" onclick="window.history.back()">← 返回</button>
      <h2 style="display:inline-block;margin-left:16px;">策略绩效分析</h2>
    </div>
    <div id="performanceContent">
      <p>加载中...</p>
    </div>
  `);
  loadPerformance(backtestId);
}

async function loadPerformance(id) {
  try {
    const data = await api('GET', `/backtest-results/${id}`);
    state.currentBacktestDetail = data;
    const result = data.result_data;
    if (data.type !== 'full') {
      document.getElementById('performanceContent').innerHTML = '<div class="card">该回测不是绩效分析，无法展示详细指标。</div>';
      return;
    }
    let html = `
      <div class="metric-row">
        <div class="metric-card"><div class="metric-label">总收益率</div><div class="metric-value ${result.total_return_pct >= 0 ? 'positive' : 'negative'}">${result.total_return_pct}%</div></div>
        <div class="metric-card"><div class="metric-label">年化收益率</div><div class="metric-value ${result.annual_return_pct >= 0 ? 'positive' : 'negative'}">${result.annual_return_pct}%</div></div>
        <div class="metric-card"><div class="metric-label">最大回撤</div><div class="metric-value negative">${result.max_drawdown_pct}%</div></div>
        <div class="metric-card"><div class="metric-label">夏普比率</div><div class="metric-value positive">${result.sharpe_ratio}</div></div>
        <div class="metric-card"><div class="metric-label">胜率</div><div class="metric-value positive">${result.win_rate_pct}%</div></div>
        <div class="metric-card"><div class="metric-label">交易次数</div><div class="metric-value">${result.num_trades}</div></div>
      </div>
      <div class="chart-container" style="height:400px;">
        <h3>净值曲线</h3>
        <canvas id="netValueChart"></canvas>
      </div>
      <div class="chart-container" style="height:400px;">
        <h3>回撤曲线</h3>
        <canvas id="drawdownChart"></canvas>
      </div>
      <div class="card">
        <h3>交易明细</h3>
        <div style="max-height:400px;overflow-y:auto;">
          <table>
            <thead><tr><th>日期</th><th>操作</th><th>价格</th><th>数量</th><th>盈亏</th></tr></thead>
            <tbody>
              ${result.transactions.map(t => `
                <tr>
                  <td>${t.date}</td>
                  <td>${t.action}</td>
                  <td>${t.price}</td>
                  <td>${t.shares}</td>
                  <td style="color:${t.pnl >= 0 ? 'green' : 'red'};">${t.pnl}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
    document.getElementById('performanceContent').innerHTML = html;
    // Draw charts
    if (window.Chart) {
      // Net value chart
      const netCtx = document.getElementById('netValueChart').getContext('2d');
      if (state.charts.netValue) state.charts.netValue.destroy();
      state.charts.netValue = new Chart(netCtx, {
        type: 'line',
        data: {
          labels: result.net_value_curve.map(p => p.date),
          datasets: [{
            label: '净值',
            data: result.net_value_curve.map(p => p.value),
            borderColor: '#1890ff',
            fill: false,
            tension: 0.1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
      // Drawdown chart
      const ddCtx = document.getElementById('drawdownChart').getContext('2d');
      if (state.charts.drawdown) state.charts.drawdown.destroy();
      state.charts.drawdown = new Chart(ddCtx, {
        type: 'line',
        data: {
          labels: result.drawdown_curve.map(p => p.date),
          datasets: [{
            label: '回撤 (%)',
            data: result.drawdown_curve.map(p => p.value),
            borderColor: '#ff4d4f',
            fill: true,
            backgroundColor: 'rgba(255,77,79,0.1)',
            tension: 0.1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
    }
  } catch (err) {
    document.getElementById('performanceContent').innerHTML = `<div style="color:red;">加载失败: ${err.message}</div>`;
  }
}

// ===== Utility =====
// Expose functions globally for onclick handlers
window.navigate = navigate;
window.handleLogout = handleLogout;
window.handleDeleteStrategy = handleDeleteStrategy;
window.showQuickDetail = showQuickDetail;
