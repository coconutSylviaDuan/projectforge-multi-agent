import json
from pathlib import Path

from .contracts import (
    AgentTrace,
    LoadProjectResponse,
    PlanResponse,
    ProjectCodeFile,
    ProjectContext,
    ProjectDocument,
    ReviseProjectResponse,
    ReviseResponse,
    RevisionAgentOutput,
    RevisionHistoryItem,
)
from .graph import invoke_validated_agent
from .prompts import REVISION_AGENT_PROMPT
from .scaffold import GENERATED_ROOT, safe_join


DOCUMENT_FILES = [
    "README.md",
    "contracts/PRD.md",
    "contracts/UI_DESIGN.md",
    "contracts/EXECUTION_SUMMARY.md",
    "contracts/VERIFICATION_REPORT.md",
]

CODE_PATTERNS = [
    "backend/**/*.py",
    "backend/requirements.txt",
    "frontend/**/*.html",
    "frontend/**/*.css",
    "frontend/**/*.js",
    "frontend/**/*.py",
    "start.ps1",
]
MAX_CODE_FILES = 80
EXCLUDED_PARTS = {"__pycache__", "node_modules", ".venv", "venv", "dist", "build"}


def revise_plan(
    plan: PlanResponse,
    feedback: str,
    history: list[RevisionHistoryItem],
    project_context: ProjectContext | None = None,
) -> ReviseResponse:
    payload = {
        "current_plan": plan.model_dump(),
        "feedback": feedback,
        "history": [item.model_dump() for item in history],
    }
    if project_context:
        payload["project_context"] = project_context.model_dump()

    result = invoke_validated_agent(
        REVISION_AGENT_PROMPT,
        payload,
        RevisionAgentOutput,
    )
    revision = RevisionAgentOutput.model_validate(result)
    revised_plan = revision.revised_plan
    revision_trace = AgentTrace(
        agent="revision_agent",
        title="方案修订",
        summary="；".join(revision.change_summary[:3]) if revision.change_summary else "已根据用户反馈修订契约。",
        output_keys=["revised_plan", "change_summary"],
    )
    traces = [
        *revised_plan.traces,
        revision_trace,
    ]
    revised_plan = revised_plan.model_copy(update={"traces": traces})
    return ReviseResponse(
        plan=revised_plan,
        change_summary=revision.change_summary,
        follow_up_questions=revision.follow_up_questions,
        traces=[revision_trace],
    )


def load_project(slug: str) -> LoadProjectResponse:
    project_dir = safe_join(GENERATED_ROOT, slug)
    plan_path = safe_join(project_dir, "contracts/plan.json")
    if not plan_path.exists():
        raise FileNotFoundError(f"Project plan not found: {plan_path}")

    plan = PlanResponse.model_validate(json.loads(plan_path.read_text(encoding="utf-8")))
    context = build_project_context(slug, project_dir)
    return LoadProjectResponse(plan=plan, context=context)


def revise_project(slug: str, feedback: str, history: list[RevisionHistoryItem]) -> ReviseProjectResponse:
    loaded = load_project(slug)
    revised = revise_plan(loaded.plan, feedback, history, loaded.context)
    return ReviseProjectResponse(
        plan=revised.plan,
        context=loaded.context,
        change_summary=revised.change_summary,
        follow_up_questions=revised.follow_up_questions,
        traces=revised.traces,
    )


def build_project_context(slug: str, project_dir: Path) -> ProjectContext:
    documents: list[ProjectDocument] = []
    for relative in DOCUMENT_FILES:
        path = safe_join(project_dir, relative)
        if path.exists() and path.is_file():
            documents.append(ProjectDocument(path=relative, content=read_limited(path, 20000)))

    code_files: list[ProjectCodeFile] = []
    seen: set[Path] = set()
    for pattern in CODE_PATTERNS:
        for path in project_dir.glob(pattern):
            if path in seen or not path.is_file():
                continue
            if EXCLUDED_PARTS.intersection(path.parts):
                continue
            seen.add(path)
            relative = path.relative_to(project_dir).as_posix()
            code_files.append(ProjectCodeFile(path=relative, content_preview=read_limited(path, 12000)))
            if len(code_files) >= MAX_CODE_FILES:
                break
        if len(code_files) >= MAX_CODE_FILES:
            break

    return ProjectContext(
        slug=slug,
        project_dir=str(project_dir),
        documents=documents,
        code_files=code_files,
    )


def read_limited(path: Path, limit: int) -> str:
    content = path.read_text(encoding="utf-8", errors="replace")
    if len(content) <= limit:
        return content
    return content[:limit] + "\n\n[TRUNCATED]"
