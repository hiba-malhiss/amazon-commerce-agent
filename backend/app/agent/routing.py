from typing import Literal

from langgraph.types import Send

from app.agent.state import AgentState, ToolRequestState
from app.core.settings import settings


def route_after_params_check(
    state: ToolRequestState,
) -> Literal["integration", "missing_info", "fail"]:
    return state["next_step"]


def dispatch_requests(state: AgentState) -> list[Send] | str:
    resolved = state.get("resolved_requests", [])

    # Enforce the maximum requests per message
    if len(resolved) > settings.max_requests_per_turn:
        raise ValueError(f"Maximum {settings.max_requests_per_turn} requests allowed per message")

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
