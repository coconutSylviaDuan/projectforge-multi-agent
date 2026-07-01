# ProjectForge Multi-Agent

AI 项目生成工作台。输入一句业务需求，系统通过 LangGraph 调度多个 Agent，先生成需求契约、UI 契约、后端/API 契约、前端契约和集成契约，再按受控模板生成项目骨架。

## Agent 分工

```text
需求分析 Agent
  -> UI 分析 Agent
  -> 后端 Agent
  -> 前端 Agent
  -> 集成检查 Agent
  -> 项目骨架生成
```

## 每个 Agent 的前置材料

| Agent | 输入材料 | 输出契约 | 基建 |
|---|---|---|---|
| 需求分析 Agent | 用户需求、行业、项目类型、技术栈、范围约束 | `RequirementSpec` | MVP 规则、实体/页面/流程模板、需求 JSON Schema |
| UI 分析 Agent | `RequirementSpec` | `UISpec` | 页面布局模板、组件规范、交互状态规范 |
| 后端 Agent | `RequirementSpec`、`UISpec`、技术条件 | `BackendSpec` + `ApiContract` | FastAPI 模板、SQLite 约定、OpenAPI 风格契约 |
| 前端 Agent | `RequirementSpec`、`UISpec`、`ApiContract` | `FrontendSpec` | 页面路由、API client、表单校验、状态模型规范 |
| 集成检查 Agent | 所有前序契约 | `IntegrationSpec` | 运行命令、验证步骤、文件树、演示脚本 |

## 快速运行

1. 配置 API：

```powershell
cd D:\dxy\projectforge-multi-agent
copy .env.example .env
```

编辑 `.env`：

```text
OPENAI_API_KEY=你的 API Key
OPENAI_MODEL=gpt-4o-mini
# OPENAI_BASE_URL=https://your-openai-compatible-gateway/v1
```

2. 启动服务：

```powershell
C:\Users\95853\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8770
```

3. 打开：

```text
http://127.0.0.1:8770/
```

## 示例需求

```text
请帮我基于聚宽规格，实现一个 AI 策略系统，包括 AI 多轮对话生成策略，策略回测，绩效分析。
```

系统会生成：

- 需求规格：目标用户、MVP、实体、页面、流程。
- UI 规格：页面布局、组件、状态、交互。
- 后端规格：FastAPI 服务、SQLite 模型、API 契约。
- 前端规格：路由、组件、API 调用、校验规则。
- 集成规格：启动命令、验证步骤、演示脚本、文件树。

## 目录结构

```text
projectforge-multi-agent
├─ backend
│  ├─ contracts.py     # Pydantic 契约模型
│  ├─ graph.py         # LangGraph 多 Agent 编排
│  ├─ llm_client.py    # 外部大模型 API
│  ├─ main.py          # FastAPI 入口
│  ├─ prompts.py       # Agent 系统提示词
│  └─ scaffold.py      # 受控项目骨架写入
├─ contracts
│  ├─ README.md
│  ├─ agent_contracts.md
│  └─ example_request.json
├─ generated_projects
├─ index.html
├─ app.js
├─ styles.css
└─ requirements.txt
```

## 当前边界

第一版生成的是“方案契约 + 项目骨架”，不是任由大模型直接写大量不可控代码。这样更适合企业内部演示：契约清晰、路径受控、可继续扩展到真实代码生成。
