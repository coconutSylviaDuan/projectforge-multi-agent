from pathlib import Path

from .contracts import PlanResponse, ScaffoldResponse


ROOT = Path(__file__).resolve().parents[1]
GENERATED_ROOT = ROOT / "generated_projects"


def safe_join(base: Path, relative: str) -> Path:
    candidate = (base / relative).resolve()
    if not str(candidate).startswith(str(base.resolve())):
        raise ValueError(f"Unsafe generated path: {relative}")
    return candidate


def render_readme(plan: PlanResponse) -> str:
    req = plan.requirement_spec
    return "\n".join(
        [
            f"# {req.project_name}",
            "",
            req.summary,
            "",
            "## MVP Scope",
            *[f"- {item}" for item in req.mvp_scope],
            "",
            "## Handoff Documents",
            "- `contracts/PRD.md`: product requirements, interface management, acceptance criteria, backend/frontend handoff notes.",
            "- `contracts/UI_DESIGN.md`: page-level UI design drafts for frontend implementation.",
            "- `contracts/plan.json`: full multi-agent contract payload.",
            "",
            "## Run Commands",
            *[f"- `{cmd}`" for cmd in plan.integration_spec.run_commands],
            "",
            "## Demo Script",
            *[f"- {step}" for step in plan.integration_spec.demo_script],
        ]
    )


def render_prd(plan: PlanResponse) -> str:
    prd = plan.requirement_spec.prd_document
    lines = [
        f"# {prd.title}",
        "",
        f"Version: {prd.version}",
        "",
        "## Background",
        prd.background,
        "",
        "## Goals",
        *[f"- {item}" for item in prd.goals],
        "",
        "## User Roles",
        *[f"- {item}" for item in prd.user_roles],
        "",
        "## Business Modules",
        *[f"- {item}" for item in prd.business_modules],
        "",
        "## Page Requirements",
    ]
    for page in prd.page_requirements:
        lines.extend(
            [
                f"### {page.name}",
                f"- Route: `{page.route}`",
                f"- Purpose: {page.purpose}",
                f"- Primary actions: {', '.join(page.primary_actions)}",
                "",
            ]
        )

    lines.extend(["## Interface Management", ""])
    for item in prd.interface_management:
        lines.extend(
            [
                f"### {item.module} / {item.name}",
                f"- Method: `{item.method}`",
                f"- Path: `{item.path}`",
                f"- Description: {item.description}",
                f"- Frontend usage: {item.frontend_usage}",
                f"- Backend notes: {item.backend_notes}",
                "- Request fields:",
                *[f"  - `{field.get('name', '')}` ({field.get('type', '')}): {field.get('description', '')}" for field in item.request_fields],
                "- Response fields:",
                *[f"  - `{field.get('name', '')}` ({field.get('type', '')}): {field.get('description', '')}" for field in item.response_fields],
                "",
            ]
        )

    lines.extend(
        [
            "## Data Requirements",
            *[f"- {item}" for item in prd.data_requirements],
            "",
            "## Acceptance Criteria",
            *[f"- {item}" for item in prd.acceptance_criteria],
            "",
            "## Frontend Handoff",
            *[f"- {item}" for item in prd.frontend_handoff],
            "",
            "## Backend Handoff",
            *[f"- {item}" for item in prd.backend_handoff],
            "",
        ]
    )
    return "\n".join(lines)


def render_ui_design(plan: PlanResponse) -> str:
    lines = [
        f"# UI Design Drafts - {plan.requirement_spec.project_name}",
        "",
        f"Design tone: {plan.ui_spec.design_tone}",
        f"Global layout: {plan.ui_spec.layout}",
        "",
        "## Navigation",
        *[f"- {item}" for item in plan.ui_spec.navigation],
        "",
    ]

    for draft in plan.ui_spec.ui_design_drafts:
        lines.extend(
            [
                f"## {draft.page}",
                f"- Route: `{draft.route}`",
                f"- New page: {'yes' if draft.is_new_page else 'no'}",
                "",
                "### Layout Wireframe",
                draft.layout_wireframe,
                "",
                "### Key Components",
                *[f"- {item}" for item in draft.key_components],
                "",
                "### Interaction States",
                *[f"- {item}" for item in draft.interaction_states],
                "",
                "### Visual Handoff",
                *[f"- {item}" for item in draft.visual_handoff],
                "",
                "### Frontend Handoff",
                *[f"- {item}" for item in draft.frontend_handoff],
                "",
            ]
        )

    return "\n".join(lines)


def render_backend_main(plan: PlanResponse) -> str:
    endpoints = plan.backend_spec.api_contract.endpoints
    handlers = []
    for endpoint in endpoints:
        name = endpoint.path.strip("/").replace("/", "_").replace("{", "").replace("}", "") or "root"
        method = endpoint.method.lower()
        handlers.append(
            f"""
@app.{method}("{endpoint.path}")
def {name}():
    return {{"message": "{endpoint.purpose}", "data": []}}
""".strip()
        )
    return "\n\n".join(
        [
            "from fastapi import FastAPI",
            "from fastapi.middleware.cors import CORSMiddleware",
            "",
            f"app = FastAPI(title=\"{plan.requirement_spec.project_name}\")",
            "app.add_middleware(CORSMiddleware, allow_origins=[\"*\"], allow_methods=[\"*\"], allow_headers=[\"*\"])",
            "",
            "@app.get(\"/api/health\")",
            "def health():",
            "    return {\"status\": \"ok\"}",
            "",
            *handlers,
            "",
        ]
    )


def render_frontend(plan: PlanResponse) -> str:
    nav = "".join(f"<button>{page.name}</button>" for page in plan.requirement_spec.pages)
    goals = "".join(f"<li>{goal}</li>" for goal in plan.requirement_spec.core_goals)
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{plan.requirement_spec.project_name}</title>
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <main>
      <aside>{nav}</aside>
      <section>
        <h1>{plan.requirement_spec.project_name}</h1>
        <p>{plan.requirement_spec.summary}</p>
        <h2>核心目标</h2>
        <ul>{goals}</ul>
        <pre id="apiResult">点击按钮测试后端接口。</pre>
        <button id="testApi">测试 /api/health</button>
      </section>
    </main>
    <script>
      document.querySelector("#testApi").addEventListener("click", async () => {{
        const res = await fetch("/api/health");
        document.querySelector("#apiResult").textContent = JSON.stringify(await res.json(), null, 2);
      }});
    </script>
  </body>
</html>
"""


def render_styles() -> str:
    return """body {
  margin: 0;
  background: #f5f7fb;
  color: #172033;
  font-family: "Microsoft YaHei", Arial, sans-serif;
}
main {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
}
aside {
  display: grid;
  align-content: start;
  gap: 10px;
  padding: 20px;
  border-right: 1px solid #dbe3ee;
  background: #fff;
}
button {
  min-height: 38px;
  border: 1px solid #dbe3ee;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
}
section {
  padding: 28px;
}
pre {
  padding: 16px;
  border: 1px solid #dbe3ee;
  border-radius: 8px;
  background: #fff;
}
"""


def scaffold_project(plan: PlanResponse, slug: str) -> ScaffoldResponse:
    target = safe_join(GENERATED_ROOT, slug)
    files = {
        "README.md": render_readme(plan),
        "backend/main.py": render_backend_main(plan),
        "backend/requirements.txt": "fastapi>=0.115.0\nuvicorn>=0.30.0\npython-jose[cryptography]==3.5.0\n",
        "frontend/index.html": render_frontend(plan),
        "frontend/styles.css": render_styles(),
        "contracts/PRD.md": render_prd(plan),
        "contracts/UI_DESIGN.md": render_ui_design(plan),
        "contracts/plan.json": plan.model_dump_json(indent=2),
    }
    written: list[str] = []
    for relative, content in files.items():
        file_path = safe_join(target, relative)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        written.append(str(file_path))
    return ScaffoldResponse(
        project_dir=str(target),
        files=written,
        message="项目骨架已生成。当前版本写入契约、README、前端页面和 FastAPI 后端骨架。",
    )
