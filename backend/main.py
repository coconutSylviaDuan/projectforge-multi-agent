from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .contracts import (
    ExecuteRequest,
    ExecuteResponse,
    GenerationRequest,
    LoadProjectRequest,
    LoadProjectResponse,
    PlanResponse,
    ReviseProjectRequest,
    ReviseProjectResponse,
    ReviseRequest,
    ReviseResponse,
    ScaffoldRequest,
    ScaffoldResponse,
)
from .executor import execute_contracts
from .graph import run_plan
from .revision import load_project, revise_plan, revise_project
from .scaffold import scaffold_project


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

app = FastAPI(title="ProjectForge Multi-Agent API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "projectforge-multi-agent"}


@app.post("/api/plan", response_model=PlanResponse)
def create_plan(request: GenerationRequest) -> PlanResponse:
    try:
        return run_plan(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/scaffold", response_model=ScaffoldResponse)
def scaffold(request: ScaffoldRequest) -> ScaffoldResponse:
    try:
        return scaffold_project(request.plan, request.slug)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/execute", response_model=ExecuteResponse)
def execute(request: ExecuteRequest) -> ExecuteResponse:
    try:
        return execute_contracts(request.plan, request.slug, request.target)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/revise", response_model=ReviseResponse)
def revise(request: ReviseRequest) -> ReviseResponse:
    try:
        return revise_plan(request.plan, request.feedback, request.history)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/load-project", response_model=LoadProjectResponse)
def load_existing_project(request: LoadProjectRequest) -> LoadProjectResponse:
    try:
        return load_project(request.slug)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/revise-project", response_model=ReviseProjectResponse)
def revise_existing_project(request: ReviseProjectRequest) -> ReviseProjectResponse:
    try:
        return revise_project(request.slug, request.feedback, request.history)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


app.mount("/contracts", StaticFiles(directory=ROOT / "contracts"), name="contracts")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT / "index.html")


@app.get("/{path:path}")
def static_files(path: str) -> FileResponse:
    file_path = ROOT / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(ROOT / "index.html")
