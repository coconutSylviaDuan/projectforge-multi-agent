from pathlib import Path
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .contracts import (
    AgentTrace,
    ExecuteResponse,
    ExecutorAgentResult,
    GeneratedFile,
    PlanResponse,
    VerificationReport,
)
from .graph import invoke_validated_agent
from .prompts import (
    BACKEND_EXECUTOR_AGENT_PROMPT,
    FRONTEND_EXECUTOR_AGENT_PROMPT,
    INTEGRATION_EXECUTOR_AGENT_PROMPT,
    VERIFICATION_REPORT_AGENT_PROMPT,
)
from .scaffold import GENERATED_ROOT, safe_join, scaffold_project


class ExecuteState(TypedDict, total=False):
    plan: dict[str, Any]
    slug: str
    target: str
    project_dir: str
    backend_result: dict[str, Any]
    frontend_result: dict[str, Any]
    integration_result: dict[str, Any]
    verification_report: dict[str, Any]
    traces: list[dict[str, Any]]
    files: list[str]


def add_trace(state: ExecuteState, agent: str, title: str, summary: str, output_keys: list[str]) -> list[dict[str, Any]]:
    return [
        *state.get("traces", []),
        AgentTrace(agent=agent, title=title, summary=summary, output_keys=output_keys).model_dump(),
    ]


def write_agent_files(project_dir: Path, files: list[dict[str, Any]]) -> list[str]:
    written: list[str] = []
    for item in files:
        generated = GeneratedFile.model_validate(item)
        file_path = safe_join(project_dir, generated.path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(generated.content, encoding="utf-8")
        written.append(str(file_path))
    return written


def apply_known_fixups(project_dir: Path) -> list[str]:
    touched: list[str] = []
    requirements = project_dir / "backend" / "requirements.txt"
    auth_files = [
        project_dir / "backend" / "app" / "auth.py",
        project_dir / "backend" / "app" / "routers" / "auth.py",
        project_dir / "backend" / "auth.py",
        project_dir / "backend" / "routers" / "auth.py",
    ]
    if any(path.exists() and "jose" in path.read_text(encoding="utf-8", errors="ignore") for path in auth_files):
        requirements.parent.mkdir(parents=True, exist_ok=True)
        content = requirements.read_text(encoding="utf-8") if requirements.exists() else ""
        if "python-jose" not in content:
            suffix = "" if content.endswith("\n") or not content else "\n"
            requirements.write_text(f"{content}{suffix}python-jose[cryptography]==3.5.0\n", encoding="utf-8")
            touched.append(str(requirements))

    for path in auth_files:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        updated = content.replace('create_access_token(data={"sub": user.id})', 'create_access_token(data={"sub": str(user.id)})')
        updated = updated.replace("create_access_token(data={'sub': user.id})", "create_access_token(data={'sub': str(user.id)})")
        updated = updated.replace("user_id: int = payload.get(\"sub\")", "user_id_str: str = payload.get(\"sub\")")
        updated = updated.replace("user_id: int = payload.get('sub')", "user_id_str: str = payload.get('sub')")
        updated = updated.replace("if user_id is None:", "if user_id_str is None:")
        updated = updated.replace("User.id == user_id", "User.id == int(user_id_str)")
        if updated != content:
            path.write_text(updated, encoding="utf-8")
            touched.append(str(path))

    index = project_dir / "frontend" / "index.html"
    if index.exists():
        content = index.read_text(encoding="utf-8")
        updated = content.replace('href="/frontend/styles.css"', 'href="/styles.css"')
        updated = updated.replace("href='/frontend/styles.css'", "href='/styles.css'")
        updated = updated.replace('src="/frontend/app.js"', 'src="/app.js"')
        updated = updated.replace("src='/frontend/app.js'", "src='/app.js'")
        if updated != content:
            index.write_text(updated, encoding="utf-8")
            touched.append(str(index))

    app_js = project_dir / "frontend" / "app.js"
    if app_js.exists():
        content = app_js.read_text(encoding="utf-8")
        updated = content.replace("const BASE = 'http://localhost:8000/api';", "const BASE = '/api';")
        updated = updated.replace('const BASE = "http://localhost:8000/api";', 'const BASE = "/api";')
        if updated != content:
            app_js.write_text(updated, encoding="utf-8")
            touched.append(str(app_js))

    proxy = project_dir / "frontend" / "dev_proxy.py"
    if not proxy.exists():
        proxy.write_text(render_frontend_proxy(), encoding="utf-8")
        touched.append(str(proxy))

    start = project_dir / "start.ps1"
    start_content = render_start_script()
    if not start.exists() or "dev_proxy.py" not in start.read_text(encoding="utf-8", errors="ignore"):
        start.write_text(start_content, encoding="utf-8")
        touched.append(str(start))
    return touched


def render_frontend_proxy() -> str:
    return '''from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import os


BACKEND = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")


class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            self.proxy()
            return
        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy()
            return
        self.send_error(404, "Not Found")

    def do_PUT(self):
        if self.path.startswith("/api/"):
            self.proxy()
            return
        self.send_error(404, "Not Found")

    def do_PATCH(self):
        if self.path.startswith("/api/"):
            self.proxy()
            return
        self.send_error(404, "Not Found")

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            self.proxy()
            return
        self.send_error(404, "Not Found")

    def proxy(self):
        body = None
        length = self.headers.get("Content-Length")
        if length:
            body = self.rfile.read(int(length))

        headers = {key: value for key, value in self.headers.items() if key.lower() != "host"}
        request = Request(f"{BACKEND}{self.path}", data=body, headers=headers, method=self.command)
        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read()
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in {"transfer-encoding", "connection"}:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(payload)
        except HTTPError as exc:
            payload = exc.read()
            self.send_response(exc.code)
            for key, value in exc.headers.items():
                if key.lower() not in {"transfer-encoding", "connection"}:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(payload)
        except URLError as exc:
            self.send_error(502, f"Backend proxy failed: {exc}")


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    server = ThreadingHTTPServer(("127.0.0.1", 5173), ProxyHandler)
    print("Frontend proxy: http://127.0.0.1:5173 -> " + BACKEND)
    server.serve_forever()
'''


def render_start_script() -> str:
    return """$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "C:\\Users\\95853\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe"
if (!(Test-Path $Python)) {
  $Python = "python"
}

$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"

Write-Host "Starting backend on http://localhost:8000"
Start-Process -FilePath $Python -ArgumentList "-m uvicorn main:app --host 127.0.0.1 --port 8000" -WorkingDirectory $Backend

Write-Host "Starting frontend proxy on http://localhost:5173"
Start-Process -FilePath $Python -ArgumentList "dev_proxy.py" -WorkingDirectory $Frontend

Write-Host "Backend:  http://localhost:8000"
Write-Host "Frontend: http://localhost:5173"
Write-Host "Proxy:    http://localhost:5173/api -> http://localhost:8000/api"
"""


def bootstrap_node(state: ExecuteState) -> dict[str, Any]:
    plan = PlanResponse.model_validate(state["plan"])
    scaffold = scaffold_project(plan, state["slug"])
    return {
        "project_dir": scaffold.project_dir,
        "files": scaffold.files,
        "traces": add_trace(
            state,
            "contract_loader",
            "契约装载",
            "已写入 PRD、UI 设计稿和完整 plan.json，准备执行契约。",
            ["project_dir", "contracts"],
        ),
    }


def backend_executor_node(state: ExecuteState) -> dict[str, Any]:
    if state.get("target") not in {"all", "backend"}:
        return {}

    result = invoke_validated_agent(
        BACKEND_EXECUTOR_AGENT_PROMPT,
        {
            "plan": state["plan"],
            "project_dir": state["project_dir"],
            "contract_files": ["contracts/PRD.md", "contracts/plan.json"],
        },
        ExecutorAgentResult,
    )
    written = write_agent_files(Path(state["project_dir"]), result.model_dump()["files"])
    return {
        "backend_result": result.model_dump(),
        "files": [*state.get("files", []), *written],
        "traces": add_trace(state, result.agent, "后端执行", result.summary, ["backend_result", "backend_files"]),
    }


def frontend_executor_node(state: ExecuteState) -> dict[str, Any]:
    if state.get("target") not in {"all", "frontend"}:
        return {}

    result = invoke_validated_agent(
        FRONTEND_EXECUTOR_AGENT_PROMPT,
        {
            "plan": state["plan"],
            "backend_result": state.get("backend_result"),
            "project_dir": state["project_dir"],
            "contract_files": ["contracts/PRD.md", "contracts/UI_DESIGN.md", "contracts/plan.json"],
        },
        ExecutorAgentResult,
    )
    written = write_agent_files(Path(state["project_dir"]), result.model_dump()["files"])
    return {
        "frontend_result": result.model_dump(),
        "files": [*state.get("files", []), *written],
        "traces": add_trace(state, result.agent, "前端执行", result.summary, ["frontend_result", "frontend_files"]),
    }


def integration_executor_node(state: ExecuteState) -> dict[str, Any]:
    if state.get("target") not in {"all", "integration"}:
        return {}

    result = invoke_validated_agent(
        INTEGRATION_EXECUTOR_AGENT_PROMPT,
        {
            "plan": state["plan"],
            "backend_result": state.get("backend_result"),
            "frontend_result": state.get("frontend_result"),
            "project_dir": state["project_dir"],
        },
        ExecutorAgentResult,
    )
    written = write_agent_files(Path(state["project_dir"]), result.model_dump()["files"])
    return {
        "integration_result": result.model_dump(),
        "files": [*state.get("files", []), *written],
        "traces": add_trace(
            state,
            result.agent,
            "集成执行",
            result.summary,
            ["integration_result", "integration_files"],
        ),
    }


def verification_report_node(state: ExecuteState) -> dict[str, Any]:
    fixup_files = apply_known_fixups(Path(state["project_dir"]))
    files_for_report = [*state.get("files", []), *fixup_files]
    report = invoke_validated_agent(
        VERIFICATION_REPORT_AGENT_PROMPT,
        {
            "plan": state["plan"],
            "target": state.get("target", "all"),
            "project_dir": state["project_dir"],
            "files": files_for_report,
            "known_fixups_applied": fixup_files,
            "backend_result": state.get("backend_result"),
            "frontend_result": state.get("frontend_result"),
            "integration_result": state.get("integration_result"),
        },
        VerificationReport,
    )

    report_path = safe_join(Path(state["project_dir"]), "contracts/VERIFICATION_REPORT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_verification_report(report), encoding="utf-8")

    return {
        "verification_report": report.model_dump(),
        "files": [*files_for_report, str(report_path)],
        "traces": add_trace(
            state,
            "verification_report_agent",
            "验证报告",
            report.summary,
            ["verification_report"],
        ),
    }


def render_verification_report(report: VerificationReport) -> str:
    return "\n".join(
        [
            "# Verification Report",
            "",
            report.summary,
            "",
            "## Completed",
            *[f"- {item}" for item in report.completed],
            "",
            "## Warnings",
            *[f"- {item}" for item in report.warnings],
            "",
            "## Next Steps",
            *[f"- {item}" for item in report.next_steps],
            "",
        ]
    )


def build_execute_graph():
    graph = StateGraph(ExecuteState)
    graph.add_node("bootstrap", bootstrap_node)
    graph.add_node("backend_executor", backend_executor_node)
    graph.add_node("frontend_executor", frontend_executor_node)
    graph.add_node("integration_executor", integration_executor_node)
    graph.add_node("verification_report", verification_report_node)

    graph.add_edge(START, "bootstrap")
    graph.add_edge("bootstrap", "backend_executor")
    graph.add_edge("backend_executor", "frontend_executor")
    graph.add_edge("frontend_executor", "integration_executor")
    graph.add_edge("integration_executor", "verification_report")
    graph.add_edge("verification_report", END)
    return graph.compile()


execute_graph = build_execute_graph()


def execute_contracts(plan: PlanResponse, slug: str, target: str = "all") -> ExecuteResponse:
    final_state = execute_graph.invoke(
        {
            "plan": plan.model_dump(),
            "slug": slug,
            "target": target,
            "traces": [],
            "files": [],
        }
    )
    return ExecuteResponse(
        project_dir=final_state.get("project_dir", str((GENERATED_ROOT / slug).resolve())),
        files=final_state.get("files", []),
        backend_result=ExecutorAgentResult.model_validate(final_state["backend_result"])
        if final_state.get("backend_result")
        else None,
        frontend_result=ExecutorAgentResult.model_validate(final_state["frontend_result"])
        if final_state.get("frontend_result")
        else None,
        integration_result=ExecutorAgentResult.model_validate(final_state["integration_result"])
        if final_state.get("integration_result")
        else None,
        verification_report=VerificationReport.model_validate(final_state["verification_report"]),
        traces=[AgentTrace.model_validate(item) for item in final_state["traces"]],
    )
