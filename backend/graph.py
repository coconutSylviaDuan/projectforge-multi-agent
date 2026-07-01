import json
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, ValidationError

from .contracts import (
    AgentTrace,
    ApiContract,
    BackendSpec,
    FrontendSpec,
    GenerationRequest,
    IntegrationSpec,
    PlanResponse,
    RequirementSpec,
    UISpec,
)
from .llm_client import build_llm, parse_json_object
from .prompts import (
    BACKEND_AGENT_PROMPT,
    FRONTEND_AGENT_PROMPT,
    INTEGRATION_AGENT_PROMPT,
    REQUIREMENT_AGENT_PROMPT,
    UI_AGENT_PROMPT,
)


class ForgeState(TypedDict, total=False):
    request: dict[str, Any]
    requirement_spec: dict[str, Any]
    ui_spec: dict[str, Any]
    frontend_spec: dict[str, Any]
    backend_spec: dict[str, Any]
    integration_spec: dict[str, Any]
    traces: list[dict[str, Any]]


def invoke_json_agent(
    system_prompt: str,
    payload: dict[str, Any],
    schema_model: type[BaseModel],
    previous_error: str | None = None,
    previous_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    llm = build_llm()
    retry_context = ""
    if previous_error:
        retry_context = (
            "\n\nYour previous output failed validation. Fix the JSON shape only.\n"
            f"Validation error:\n{previous_error}\n"
            f"Previous output:\n{json.dumps(previous_output, ensure_ascii=False)}"
        )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                "Return one JSON object only. Do not use Markdown or explanations.\n"
                "The JSON must validate against this JSON Schema exactly. "
                "Use arrays where the schema says array, and include all required fields.\n"
                f"JSON Schema:\n{json.dumps(schema_model.model_json_schema(), ensure_ascii=False)}\n\n"
                f"Input context:\n{json.dumps(payload, ensure_ascii=False)}"
                f"{retry_context}"
            )
        ),
    ]
    return parse_json_object(str(llm.invoke(messages).content))


def invoke_validated_agent(system_prompt: str, payload: dict[str, Any], schema_model: type[BaseModel]) -> BaseModel:
    previous_output: dict[str, Any] | None = None
    previous_error: str | None = None
    last_error: Exception | None = None

    for _ in range(3):
        parsed: dict[str, Any] | None = None
        try:
            parsed = invoke_json_agent(system_prompt, payload, schema_model, previous_error, previous_output)
            return schema_model.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as exc:
            if parsed is not None:
                previous_output = parsed
            previous_error = str(exc)
            last_error = exc

    if last_error:
        raise last_error
    raise RuntimeError(f"{schema_model.__name__} validation failed")


def add_trace(state: ForgeState, agent: str, title: str, summary: str, output_keys: list[str]) -> list[dict[str, Any]]:
    return [
        *state.get("traces", []),
        AgentTrace(agent=agent, title=title, summary=summary, output_keys=output_keys).model_dump(),
    ]


def requirement_node(state: ForgeState) -> dict[str, Any]:
    spec = invoke_validated_agent(REQUIREMENT_AGENT_PROMPT, {"request": state["request"]}, RequirementSpec)
    return {
        "requirement_spec": spec.model_dump(),
        "traces": add_trace(
            state,
            "需求分析 Agent",
            "需求规格与 PRD",
            spec.summary,
            ["requirement_spec", "prd_document"],
        ),
    }


def ui_node(state: ForgeState) -> dict[str, Any]:
    spec = invoke_validated_agent(
        UI_AGENT_PROMPT,
        {
            "requirement_spec": state["requirement_spec"],
            "prd_document": state["requirement_spec"].get("prd_document"),
        },
        UISpec,
    )
    return {
        "ui_spec": spec.model_dump(),
        "traces": add_trace(
            state,
            "UI 分析 Agent",
            "UI 规格与设计稿",
            spec.design_tone,
            ["ui_spec", "ui_design_drafts"],
        ),
    }


def backend_node(state: ForgeState) -> dict[str, Any]:
    spec = invoke_validated_agent(
        BACKEND_AGENT_PROMPT,
        {
            "request": state["request"],
            "requirement_spec": state["requirement_spec"],
            "prd_document": state["requirement_spec"].get("prd_document"),
            "ui_spec": state["ui_spec"],
        },
        BackendSpec,
    )
    return {
        "backend_spec": spec.model_dump(),
        "traces": add_trace(state, "后端 Agent", "后端与 API 契约", spec.framework, ["backend_spec", "api_contract"]),
    }


def frontend_node(state: ForgeState) -> dict[str, Any]:
    api_contract = ApiContract.model_validate(state["backend_spec"]["api_contract"]).model_dump()
    spec = invoke_validated_agent(
        FRONTEND_AGENT_PROMPT,
        {
            "requirement_spec": state["requirement_spec"],
            "prd_document": state["requirement_spec"].get("prd_document"),
            "ui_spec": state["ui_spec"],
            "ui_design_drafts": state["ui_spec"].get("ui_design_drafts"),
            "api_contract": api_contract,
        },
        FrontendSpec,
    )
    return {
        "frontend_spec": spec.model_dump(),
        "traces": add_trace(state, "前端 Agent", "前端实现规格", spec.framework, ["frontend_spec"]),
    }


def integration_node(state: ForgeState) -> dict[str, Any]:
    spec = invoke_validated_agent(
        INTEGRATION_AGENT_PROMPT,
        {
            "requirement_spec": state["requirement_spec"],
            "prd_document": state["requirement_spec"].get("prd_document"),
            "ui_spec": state["ui_spec"],
            "ui_design_drafts": state["ui_spec"].get("ui_design_drafts"),
            "frontend_spec": state["frontend_spec"],
            "backend_spec": state["backend_spec"],
        },
        IntegrationSpec,
    )
    return {
        "integration_spec": spec.model_dump(),
        "traces": add_trace(
            state,
            "集成检查 Agent",
            "集成与演示方案",
            "PRD、UI 设计稿、前后端契约对齐与运行说明",
            ["integration_spec"],
        ),
    }


def build_graph():
    graph = StateGraph(ForgeState)
    graph.add_node("requirements", requirement_node)
    graph.add_node("ui", ui_node)
    graph.add_node("backend", backend_node)
    graph.add_node("frontend", frontend_node)
    graph.add_node("integration", integration_node)

    graph.add_edge(START, "requirements")
    graph.add_edge("requirements", "ui")
    graph.add_edge("ui", "backend")
    graph.add_edge("backend", "frontend")
    graph.add_edge("frontend", "integration")
    graph.add_edge("integration", END)
    return graph.compile()


forge_graph = build_graph()


def run_plan(request: GenerationRequest) -> PlanResponse:
    final_state = forge_graph.invoke({"request": request.model_dump(), "traces": []})
    return PlanResponse(
        request=request,
        requirement_spec=RequirementSpec.model_validate(final_state["requirement_spec"]),
        ui_spec=UISpec.model_validate(final_state["ui_spec"]),
        frontend_spec=FrontendSpec.model_validate(final_state["frontend_spec"]),
        backend_spec=BackendSpec.model_validate(final_state["backend_spec"]),
        integration_spec=IntegrationSpec.model_validate(final_state["integration_spec"]),
        traces=[AgentTrace.model_validate(item) for item in final_state["traces"]],
    )
