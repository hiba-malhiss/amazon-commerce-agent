from typing import Literal

from langgraph.types import Send

from app.agent.state import AgentState, ToolRequestState
from app.configurations.integrations.registry import INTEGRATIONS_BY_CODE
from app.configurations.schemas import RAGIntegrationConfig
from app.configurations.tools.registry import TOOLS_BY_CODE

type ToolRoute = Literal["api_call", "rag_search", "missing_info", "fail"]


def route_after_params_check(state: ToolRequestState) -> ToolRoute:
    """Missing parameters or a failed check end there; a ready tool runs the way its
    integration works: a document search for RAG, an API call otherwise."""
    step = state.get("next_step", "fail")
    if step != "integration":
        return step

    tool = TOOLS_BY_CODE.get(state["request"]["tool"])
    integration = INTEGRATIONS_BY_CODE.get(tool.integration_code or "") if tool else None
    return "rag_search" if isinstance(integration, RAGIntegrationConfig) else "api_call"


def dispatch_requests(state: AgentState) -> list[Send] | str:
    resolved = state.get("resolved_requests", [])

    # Dispatch ready requests independently
    sends = [
        Send(
            "tool_workflow",
            {
                "id": item["id"],
                "request": item["request"],
            },
        )
        for item in resolved
        if item["status"] == "ready"
    ]

    return sends if sends else "collect"
