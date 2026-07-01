from typing import Literal

from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    user_request: str = Field(..., min_length=8)
    industry: str = "证券金融"
    project_type: str = "业务系统"
    tech_stack: str = "FastAPI + SQLite + HTML/CSS/JS"
    needs_auth: bool = False
    needs_database: bool = True
    needs_external_api: bool = True
    constraints: list[str] = Field(default_factory=lambda: ["一天内可演示", "MVP 优先", "本地可运行"])


class EntitySpec(BaseModel):
    name: str
    description: str
    fields: list[dict[str, str]]


class PageSpec(BaseModel):
    name: str
    route: str
    purpose: str
    primary_actions: list[str]


class InterfaceRequirement(BaseModel):
    module: str
    name: str
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str
    description: str
    request_fields: list[dict[str, str]] = Field(default_factory=list)
    response_fields: list[dict[str, str]] = Field(default_factory=list)
    frontend_usage: str
    backend_notes: str


class PRDDocument(BaseModel):
    title: str
    version: str = "v0.1"
    background: str
    goals: list[str]
    user_roles: list[str]
    business_modules: list[str]
    page_requirements: list[PageSpec]
    interface_management: list[InterfaceRequirement]
    data_requirements: list[str]
    acceptance_criteria: list[str]
    frontend_handoff: list[str]
    backend_handoff: list[str]


class RequirementSpec(BaseModel):
    project_name: str
    summary: str
    target_users: list[str]
    core_goals: list[str]
    mvp_scope: list[str]
    out_of_scope: list[str]
    entities: list[EntitySpec]
    pages: list[PageSpec]
    workflows: list[str]
    risks_and_assumptions: list[str]
    prd_document: PRDDocument


class UIComponentSpec(BaseModel):
    page: str
    components: list[str]
    states: list[str]
    interactions: list[str]


class UIDesignDraft(BaseModel):
    page: str
    route: str
    is_new_page: bool = True
    layout_wireframe: str
    key_components: list[str]
    interaction_states: list[str]
    visual_handoff: list[str]
    frontend_handoff: list[str]


class UISpec(BaseModel):
    design_tone: str
    layout: str
    navigation: list[str]
    component_specs: list[UIComponentSpec]
    ui_design_drafts: list[UIDesignDraft]
    visual_rules: list[str]
    accessibility_rules: list[str]


class ApiEndpointSpec(BaseModel):
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str
    purpose: str
    request_schema: dict[str, str] = Field(default_factory=dict)
    response_schema: dict[str, str] = Field(default_factory=dict)


class ApiContract(BaseModel):
    base_url: str = "/api"
    endpoints: list[ApiEndpointSpec]
    shared_types: list[dict[str, str]]
    error_shape: dict[str, str]


class FrontendSpec(BaseModel):
    framework: str
    routes: list[str]
    components: list[str]
    api_dependencies: list[str]
    state_model: list[str]
    validation_rules: list[str]
    files_to_generate: list[str]


class BackendSpec(BaseModel):
    framework: str
    database: str
    services: list[str]
    models: list[str]
    api_contract: ApiContract
    environment_variables: list[str]
    files_to_generate: list[str]


class IntegrationSpec(BaseModel):
    run_commands: list[str]
    verification_steps: list[str]
    file_tree: list[str]
    demo_script: list[str]
    generated_files: list[dict[str, str]]


class AgentTrace(BaseModel):
    agent: str
    title: str
    summary: str
    output_keys: list[str]


class GeneratedFile(BaseModel):
    path: str
    purpose: str
    content: str


class ExecutorAgentResult(BaseModel):
    agent: str
    summary: str
    files: list[GeneratedFile]
    notes: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class VerificationReport(BaseModel):
    summary: str
    completed: list[str]
    warnings: list[str]
    next_steps: list[str]


class RevisionHistoryItem(BaseModel):
    feedback: str
    change_summary: list[str]


class PlanResponse(BaseModel):
    request: GenerationRequest
    requirement_spec: RequirementSpec
    ui_spec: UISpec
    frontend_spec: FrontendSpec
    backend_spec: BackendSpec
    integration_spec: IntegrationSpec
    traces: list[AgentTrace]


class ScaffoldRequest(BaseModel):
    plan: PlanResponse
    slug: str = Field(..., pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")


class ScaffoldResponse(BaseModel):
    project_dir: str
    files: list[str]
    message: str


class ExecuteRequest(BaseModel):
    plan: PlanResponse
    slug: str = Field(..., pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")
    target: Literal["all", "backend", "frontend", "integration"] = "all"


class ExecuteResponse(BaseModel):
    project_dir: str
    files: list[str]
    backend_result: ExecutorAgentResult | None = None
    frontend_result: ExecutorAgentResult | None = None
    integration_result: ExecutorAgentResult | None = None
    verification_report: VerificationReport
    traces: list[AgentTrace]


class ReviseRequest(BaseModel):
    plan: PlanResponse
    feedback: str = Field(..., min_length=2)
    history: list[RevisionHistoryItem] = Field(default_factory=list)


class RevisionAgentOutput(BaseModel):
    revised_plan: PlanResponse
    change_summary: list[str]
    follow_up_questions: list[str] = Field(default_factory=list)


class ReviseResponse(BaseModel):
    plan: PlanResponse
    change_summary: list[str]
    follow_up_questions: list[str]
    traces: list[AgentTrace]


class ProjectDocument(BaseModel):
    path: str
    content: str


class ProjectCodeFile(BaseModel):
    path: str
    content_preview: str


class ProjectContext(BaseModel):
    slug: str
    project_dir: str
    documents: list[ProjectDocument]
    code_files: list[ProjectCodeFile]


class LoadProjectRequest(BaseModel):
    slug: str = Field(..., pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")


class LoadProjectResponse(BaseModel):
    plan: PlanResponse
    context: ProjectContext


class ReviseProjectRequest(BaseModel):
    slug: str = Field(..., pattern=r"^[a-z0-9][a-z0-9-]{1,60}$")
    feedback: str = Field(..., min_length=2)
    history: list[RevisionHistoryItem] = Field(default_factory=list)


class ReviseProjectResponse(BaseModel):
    plan: PlanResponse
    context: ProjectContext
    change_summary: list[str]
    follow_up_questions: list[str]
    traces: list[AgentTrace]
