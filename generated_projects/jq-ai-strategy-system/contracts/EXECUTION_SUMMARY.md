# 集成执行摘要

## 后端执行

- **框架**: FastAPI + SQLAlchemy + SQLite
- **认证**: JWT（PyJWT + bcrypt），依赖注入 `get_current_user` 保护所有非公开接口。
- **数据库模型**: User、Strategy、BacktestResult，对应 PRD 实体设计。
- **接口列表**:
  - `POST /api/auth/register` - 用户注册
  - `POST /api/auth/login` - 用户登录
  - `POST /api/chat/generate` - AI 生成策略代码（模拟）
  - `POST /api/chat/continue` - 多轮对话继续（模拟）
  - `POST /api/strategies` - 创建或更新策略
  - `GET /api/strategies` - 获取策略列表
  - `GET /api/strategies/{id}` - 获取策略详情
  - `DELETE /api/strategies/{id}` - 删除策略
  - `POST /api/backtest/quick` - 快速回测（模拟）
  - `POST /api/backtest/analysis` - 完整回测绩效分析（模拟）
  - `GET /api/backtest-results` - 查询回测结果列表（支持 type 过滤）
  - `GET /api/backtest-results/{id}` - 获取回测结果详情
- **服务**: `ai_service.py` 模拟 AI 生成代码（固定双均线策略）和对话修改（简单替换参数）；`backtest_engine.py` 使用随机数据模拟回测指标。
- **注意事项**: JWT secret 硬编码（生产应使用环境变量）；数据库使用 SQLite；所有模拟数据不具有实际投资参考价值。

## 前端执行

- **架构**: 原生 JavaScript SPA，客户端 hash 路由，无构建工具。
- **CDN 依赖**: CodeMirror (代码编辑器), Chart.js (图表)。
- **页面路由**:
  - `/login` - 登录页面
  - `/register` - 注册页面
  - `/` - 首页（AI 对话生成）
  - `/strategy/edit/:id` - 策略编辑页
  - `/strategies` - 策略列表页
  - `/backtest-results` - 回测结果列表页
  - `/strategy/performance/:backtestId` - 绩效分析页
- **核心交互**:
  - 登录/注册成功后 token 存入 localStorage，后续 API 自动添加 Authorization 头。
  - 主页输入框回车调用 `POST /api/chat/generate`，成功后可预览代码并自动跳转到编辑页。
  - 编辑页包含 CodeMirror 编辑器、多轮对话面板、快速回测结果标签页。
  - 保存策略、快速回测、运行完整回测功能通过顶部按钮触发。
  - 多轮对话调用 `POST /api/chat/continue`，返回新代码并更新编辑器。
  - 快速回测结果和绩效分析页使用 Chart.js 渲染净值曲线和回撤曲线。
- **注意事项**: 编辑器使用 CodeMirror 而非 Monaco（简化 CDN 加载）；无状态管理库（全部在全局对象中）。

## 集成对齐

- 前端所有 API 调用路径均与后端路由一致（如 `/api/strategies`）。
- 请求/响应格式匹配：前端发送 JSON，后端解析 Pydantic 模型，返回 JSON。
- 认证流程对齐：后端返回 `access_token`，前端存储在 `localStorage`，通过 `Authorization: Bearer <token>` 传递。
- CORS：后端允许 `http://localhost:5173` 和 `http://127.0.0.1:5173`，前端在同一域名下运行（或通过代理）。
- 错误处理：后端返回 4xx/5xx 状态码和 `detail` 字段，前端捕获并显示。
- 数据完整性：策略创建和更新通过 `POST /api/strategies` 实现；回测结果绑定策略在 `POST /api/backtest/analysis` 中完成。
- 模拟服务：AI 和回测引擎为本地模拟，无需真实聚宽 SDK 或 OpenAI API。

## 已知差异与风险

1. **前端无构建工具**：当前为静态 HTML+JS，开发体验不如 Vite/React，但可直接在浏览器中运行。
2. **编辑器非 Monaco**：技术方案使用 CodeMirror 替代，功能上可满足 Python 代码编辑，但 UI 规格中推荐的 Monaco 未使用。
3. **无分页与搜索**：后端列表接口未实现分页，前端也未处理大量数据。
4. **安全加固缺失**：无 HTTPS、CSRF 防护、输入 XSS 过滤（仅用于演示）。
5. **模拟数据随机**：回测结果每次不同，不满足一致性要求，但演示功能逻辑足够。

---
*此文档由 intergration_executor_agent 自动生成。*
