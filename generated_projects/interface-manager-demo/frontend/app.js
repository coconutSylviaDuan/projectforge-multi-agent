const API_BASE = '/api';
let state = {
    interfaces: [],
    total: 0,
    page: 1,
    pageSize: 20,
    filterMethod: '',
    currentInterfaceId: null,
    currentTab: 'mock',
    loading: false,
    error: ''
};

function navigate(hash) {
    window.location.hash = hash;
}

async function fetchJSON(url, options = {}) {
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options
    });
    if (!res.ok) {
        let errMsg = res.statusText;
        try {
            const err = await res.json();
            errMsg = err.detail || err.error || errMsg;
        } catch (_) {}
        throw new Error(errMsg);
    }
    return res.json();
}

function render(html) {
    document.getElementById('app').innerHTML = html;
}

function showLoading() {
    render('<div class="text-center mt-5"><div class="spinner-border" role="status"><span class="visually-hidden">加载中...</span></div></div>');
}

function showError(message) {
    render(`<div class="alert alert-danger">${message}</div>`);
}

function formatDate(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return isNaN(d.getTime()) ? iso : d.toLocaleString();
}

function methodBadge(method) {
    return `<span class="method-badge method-${method}">${method}</span>`;
}

// ============ 路由处理 ============
window.addEventListener('hashchange', handleRoute);
window.addEventListener('load', handleRoute);

function handleRoute() {
    const hash = window.location.hash.slice(1) || '/interfaces';
    const parts = hash.split('/');
    if (parts[1] === 'interfaces') {
        if (parts[2] === undefined) {
            // 接口目录
            state.page = 1;
            renderInterfacesPage();
        } else {
            const id = parseInt(parts[2]);
            if (!isNaN(id)) {
                state.currentInterfaceId = id;
                // 确定tab
                if (parts[3] === 'mock' || parts[3] === 'changes' || parts[3] === 'integration') {
                    state.currentTab = parts[3];
                } else {
                    state.currentTab = 'mock';
                }
                renderDetailPage(id);
            } else {
                navigate('#/interfaces');
            }
        }
    } else {
        navigate('#/interfaces');
    }
}

// ============ 接口目录页 ============
async function renderInterfacesPage() {
    showLoading();
    try {
        const params = new URLSearchParams({ page: state.page, page_size: state.pageSize });
        if (state.filterMethod) params.set('method', state.filterMethod);
        const data = await fetchJSON(`${API_BASE}/interfaces?${params}`);
        state.interfaces = data.items;
        state.total = data.total;
        let html = `
            <div class="row mb-3">
                <div class="col-md-6">
                    <input type="text" class="form-control" id="searchInput" placeholder="搜索接口名称..." oninput="filterInterfaces()">
                </div>
                <div class="col-md-3">
                    <select class="form-select" id="methodFilter" onchange="state.filterMethod=this.value; state.page=1; renderInterfacesPage()">
                        <option value="">所有方法</option>
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="PUT">PUT</option>
                        <option value="DELETE">DELETE</option>
                    </select>
                </div>
            </div>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead><tr><th>方法</th><th>路径</th><th>名称</th><th>描述</th><th>更新时间</th></tr></thead>
                    <tbody id="interfaceTableBody">
        `;
        for (const item of data.items) {
            html += `<tr onclick="navigate('#/interfaces/${item.id}')" style="cursor:pointer">
                <td>${methodBadge(item.method)}</td>
                <td>${item.path}</td>
                <td><a href="#/interfaces/${item.id}" onclick="event.stopPropagation()">${item.name}</a></td>
                <td>${item.description || ''}</td>
                <td>${formatDate(item.updated_at)}</td>
            </tr>`;
        }
        html += `</tbody></table></div>`;
        // 分页
        const totalPages = Math.ceil(state.total / state.pageSize);
        html += `<nav><ul class="pagination justify-content-center">`;
        for (let i = 1; i <= totalPages; i++) {
            html += `<li class="page-item ${i === state.page ? 'active' : ''}"><a class="page-link" href="#/interfaces" onclick="state.page=${i}; renderInterfacesPage(); return false">${i}</a></li>`;
        }
        html += `</ul></nav>`;
        render(html);
        // 恢复筛选条件
        document.getElementById('methodFilter').value = state.filterMethod;
    } catch (e) {
        showError('加载接口列表失败: ' + e.message);
    }
}

// 前端搜索过滤
function filterInterfaces() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#interfaceTableBody tr');
    rows.forEach(row => {
        const name = row.cells[2].textContent.toLowerCase();
        row.style.display = name.includes(query) ? '' : 'none';
    });
}

// ============ 接口详情页 ============
async function renderDetailPage(interfaceId) {
    showLoading();
    try {
        const iface = await fetchJSON(`${API_BASE}/interfaces/${interfaceId}`);
        renderInterfaceDetail(iface, state.currentTab);
        loadTabContent(interfaceId, state.currentTab);
    } catch (e) {
        showError('加载接口详情失败: ' + e.message);
    }
}

function renderInterfaceDetail(iface, activeTab) {
    const tabs = [
        { id: 'mock', label: 'Mock配置', hash: `#/interfaces/${iface.id}/mock` },
        { id: 'changes', label: '变更记录', hash: `#/interfaces/${iface.id}/changes` },
        { id: 'integration', label: '联调状态', hash: `#/interfaces/${iface.id}/integration` }
    ];
    let tabLinks = '';
    for (const t of tabs) {
        tabLinks += `<li class="nav-item"><a class="nav-link ${t.id === activeTab ? 'active' : ''}" href="${t.hash}">${t.label}</a></li>`;
    }
    let html = `
        <nav aria-label="breadcrumb"><ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#/interfaces">接口目录</a></li>
            <li class="breadcrumb-item active">${iface.name}</li>
        </ol></nav>
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">${methodBadge(iface.method)} ${iface.name}</h5>
                <p class="card-text"><strong>路径：</strong>${iface.path}</p>
                <p class="card-text"><strong>描述：</strong>${iface.description || '无'}</p>
                <p class="card-text"><strong>请求参数：</strong><pre><code>${iface.request_params || '{}'}</code></pre></p>
                <p class="card-text"><strong>响应结构：</strong><pre><code>${iface.response_schema || '{}'}</code></pre></p>
                <p class="card-text text-muted">创建时间：${formatDate(iface.created_at)} ｜ 更新时间：${formatDate(iface.updated_at)}</p>
            </div>
        </div>
        <ul class="nav nav-tabs" id="detailTabs">${tabLinks}</ul>
        <div class="tab-content mt-3" id="tabContent">
            <div class="text-center">加载中...</div>
        </div>
    `;
    render(html);
}

async function loadTabContent(interfaceId, tab) {
    const tabContentDiv = document.getElementById('tabContent');
    if (!tabContentDiv) return;
    try {
        tabContentDiv.innerHTML = '<div class="text-center">加载中...</div>';
        let contentHtml = '';
        if (tab === 'mock') {
            const config = await fetchJSON(`${API_BASE}/interfaces/${interfaceId}/mock`);
            const enabledChecked = config.enabled ? 'checked' : '';
            contentHtml = `
                <form id="mockForm" onsubmit="saveMockConfig(event, ${interfaceId})">
                    <div class="mb-3 form-check form-switch">
                        <input class="form-check-input" type="checkbox" id="enabledSwitch" ${enabledChecked}>
                        <label class="form-check-label" for="enabledSwitch">启用Mock</label>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">状态码</label>
                        <input type="number" class="form-control" id="statusCode" value="${config.status_code}" min="100" max="599">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">响应头 (JSON)</label>
                        <textarea class="form-control monospace" id="mockHeaders" rows="3">${config.headers || '{}'}</textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">响应体 (JSON)</label>
                        <textarea class="form-control monospace" id="mockBody" rows="8">${config.body || '{}'}</textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">延迟 (ms)</label>
                        <input type="number" class="form-control" id="delayMs" value="${config.delay_ms || 0}" min="0">
                    </div>
                    <button type="submit" class="btn btn-primary" id="mockSubmitBtn">保存</button>
                    <div id="mockToast" class="mt-2"></div>
                </form>
            `;
        } else if (tab === 'changes') {
            const data = await fetchJSON(`${API_BASE}/interfaces/${interfaceId}/changes?limit=20`);
            if (data.items.length === 0) {
                contentHtml = '<div class="alert alert-info">暂无变更记录</div>';
            } else {
                let tableHtml = '<table class="table table-striped"><thead><tr><th>字段</th><th>旧值</th><th>新值</th><th>变更时间</th></tr></thead><tbody>';
                for (const log of data.items) {
                    const oldVal = log.old_value || '';
                    const newVal = log.new_value || '';
                    tableHtml += `<tr>
                        <td>${log.field}</td>
                        <td title="${oldVal.replace(/"/g, '&quot;')}">${oldVal.substring(0, 50)}${oldVal.length > 50 ? '...' : ''}</td>
                        <td title="${newVal.replace(/"/g, '&quot;')}">${newVal.substring(0, 50)}${newVal.length > 50 ? '...' : ''}</td>
                        <td>${formatDate(log.changed_at)}</td>
                    </tr>`;
                }
                tableHtml += '</tbody></table>';
                contentHtml = tableHtml;
            }
        } else if (tab === 'integration') {
            const status = await fetchJSON(`${API_BASE}/interfaces/${interfaceId}/integration`);
            const statusLabels = { '未开始': 'secondary', '联调中': 'primary', '已完成': 'success' };
            const badgeClass = statusLabels[status.status] || 'secondary';
            contentHtml = `
                <div class="mb-3">
                    <span class="badge bg-${badgeClass} status-badge">${status.status}</span>
                </div>
                <form id="integrationForm" onsubmit="saveIntegration(event, ${interfaceId})">
                    <div class="mb-3">
                        <label class="form-label">状态</label>
                        <select class="form-select" id="statusSelect">
                            <option value="未开始" ${status.status === '未开始' ? 'selected' : ''}>未开始</option>
                            <option value="联调中" ${status.status === '联调中' ? 'selected' : ''}>联调中</option>
                            <option value="已完成" ${status.status === '已完成' ? 'selected' : ''}>已完成</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">备注</label>
                        <textarea class="form-control" id="statusNotes" rows="3">${status.notes || ''}</textarea>
                    </div>
                    <button type="submit" class="btn btn-primary" id="integrationSubmitBtn">更新</button>
                    <div id="integrationToast" class="mt-2"></div>
                </form>
                <p class="text-muted mt-3">最后更新时间：${formatDate(status.updated_at)}</p>
            `;
        }
        tabContentDiv.innerHTML = contentHtml;
    } catch (e) {
        tabContentDiv.innerHTML = `<div class="alert alert-danger">加载失败: ${e.message}</div>`;
    }
}

// ============ Mock保存 ============
async function saveMockConfig(event, interfaceId) {
    event.preventDefault();
    const btn = document.getElementById('mockSubmitBtn');
    if (!btn) return;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 保存中...';
    const toast = document.getElementById('mockToast');
    try {
        const enabled = document.getElementById('enabledSwitch').checked;
        const statusCode = parseInt(document.getElementById('statusCode').value) || 200;
        const headers = document.getElementById('mockHeaders').value;
        const body = document.getElementById('mockBody').value;
        // 验证JSON
        JSON.parse(headers);
        JSON.parse(body);
        const delayMs = parseInt(document.getElementById('delayMs').value) || 0;
        await fetchJSON(`${API_BASE}/interfaces/${interfaceId}/mock`, {
            method: 'PUT',
            body: JSON.stringify({ enabled, status_code: statusCode, headers, body, delay_ms: delayMs })
        });
        toast.innerHTML = '<div class="alert alert-success">保存成功</div>';
        // 重新加载配置以更新字段
        const config = await fetchJSON(`${API_BASE}/interfaces/${interfaceId}/mock`);
        document.getElementById('enabledSwitch').checked = config.enabled;
        document.getElementById('statusCode').value = config.status_code;
        document.getElementById('mockHeaders').value = config.headers;
        document.getElementById('mockBody').value = config.body;
        document.getElementById('delayMs').value = config.delay_ms;
    } catch (e) {
        toast.innerHTML = `<div class="alert alert-danger">保存失败: ${e.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '保存';
        setTimeout(() => toast.innerHTML = '', 3000);
    }
}

// ============ 联调状态保存 ============
async function saveIntegration(event, interfaceId) {
    event.preventDefault();
    const btn = document.getElementById('integrationSubmitBtn');
    if (!btn) return;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 更新中...';
    const toast = document.getElementById('integrationToast');
    try {
        const status = document.getElementById('statusSelect').value;
        const notes = document.getElementById('statusNotes').value;
        await fetchJSON(`${API_BASE}/interfaces/${interfaceId}/integration`, {
            method: 'PUT',
            body: JSON.stringify({ status, notes })
        });
        toast.innerHTML = '<div class="alert alert-success">更新成功</div>';
        // 重新加载状态
        const newStatus = await fetchJSON(`${API_BASE}/interfaces/${interfaceId}/integration`);
        document.getElementById('statusSelect').value = newStatus.status;
        document.getElementById('statusNotes').value = newStatus.notes;
        // 更新badge
        const badgeClass = { '未开始': 'secondary', '联调中': 'primary', '已完成': 'success' }[newStatus.status] || 'secondary';
        const badge = document.querySelector('.status-badge');
        if (badge) {
            badge.className = `badge bg-${badgeClass} status-badge`;
            badge.textContent = newStatus.status;
        }
    } catch (e) {
        toast.innerHTML = `<div class="alert alert-danger">更新失败: ${e.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '更新';
        setTimeout(() => toast.innerHTML = '', 3000);
    }
}