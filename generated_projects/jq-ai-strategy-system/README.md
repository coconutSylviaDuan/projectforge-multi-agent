# AI 策略系统 (AI Strategy System)

基于 AI 多轮对话的量化策略生成与回测系统。MVP 版本可在本地完整运行。

## 技术栈
- **后端**: FastAPI + SQLite + SQLAlchemy + JWT 认证
- **前端**: 原生 JavaScript SPA (CodeMirror 编辑器, Chart.js 图表)
- **AI 对话**: 本地模拟（可替换为真实大模型 API）
- **回测引擎**: 本地模拟

## 快速启动

### 1. 启动后端

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate  |  Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python -c "from app.database import init_db; init_db()"
uvicorn app.main:app --reload --port 8000
```

后端将在 http://localhost:8000 启动，API 文档位于 http://localhost:8000/docs。

### 2. 启动前端

```bash
cd frontend
# 无需安装依赖（纯静态，仅需一个 HTTP 服务器）
# 方式一：使用 Python
python -m http.server 5173 --directory .
# 方式二：使用 Vite（推荐，可热更新）
# 但当前前端为静态文件，直接使用 Python 服务器即可
```

前端将在 http://localhost:5173 访问。

> **注意**：前端当前为 vanilla JS 应用，不需要 npm install。如果希望使用 Vite 开发模式，可在此目录下运行 `npm init -y` 和 `npm install vite --save-dev`，然后配置 vite 并运行 `npx vite`。

### 3. 访问系统

打开浏览器访问 http://localhost:5173，将自动跳转到登录页面。

## 验收清单

以下步骤为完整的验收流程，对应 PRD 的接受标准：

1. **用户注册**：访问 http://localhost:5173，未登录跳转至登录页。点击“立即注册”，输入用户名（至少3字符）和密码（至少6字符），注册成功自动登录并跳转首页。
2. **AI 生成策略**：在首页输入框输入“生成一个双均线策略”，按回车或点击发送。2 秒后自动跳转到策略编辑页（新策略已创建）。
3. **策略编辑页**：左侧显示代码编辑器（Python），右侧默认多轮对话 Tab。顶部有保存、快速回测、运行回测绩效分析按钮。
4. **多轮对话**：在对话输入框输入“把均线周期改为10和30”，发送后观察代码编辑器中的参数更新。
5. **保存策略**：点击“保存”按钮，提示保存成功，策略持久化。
6. **快速回测**：点击“快速回测”，右侧 Tab 自动切换到快速回测结果，显示指标（总收益率、年化收益率、最大回撤、夏普比率）和净值曲线图。
7. **运行回测绩效分析**：点击“运行回测绩效分析”，跳转至绩效分析页，展示总收益率、年化收益率、最大回撤、夏普比率、胜率、交易次数等指标，以及净值曲线图、回撤曲线图、交易明细表格。
8. **策略列表**：点击左侧导航“策略列表”，显示所有已保存策略，支持编辑和删除。
9. **回测结果列表**：点击左侧导航“回测结果”，显示所有回测记录，可按类型（快速/绩效分析）过滤。点击“绩效分析”记录的查看详情可进入绩效分析页。
10. **退出登录**：点击顶部“退出”按钮，清除 token，返回登录页。

## 注意事项

- 所有 API 调用需要 Bearer Token（除注册登录外）。
- 后端 CORS 已配置允许 http://localhost:5173 和 http://127.0.0.1:5173。
- 数据库为 SQLite 文件 `backend/ai_strategy.db`，首次启动自动创建表。
- AI 对话和回测引擎均为模拟实现，不依赖外部服务。
