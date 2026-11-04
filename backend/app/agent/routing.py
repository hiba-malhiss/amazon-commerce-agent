from typing import Literal

from langgraph.types import Send

from app.agent.state import AgentState, ToolRequestState, ToolStep
from app.core.settings import settings


def route_after_params_check(state: ToolRequestState) -> ToolStep:
    return state.get("next_step", "fail")


def dispatch_requests(state: AgentState) -> list[Send] | Literal["collect"]:
    resolved = state.get("resolved_requests", [])

    # Enforce the maximum requests per message
    if len(resolved) > settings.max_requests_per_turn:
        raise ValueError(f"Maximum {settings.max_requests_per_turn} requests allowed per message")

    # Dispatch ready requests independently
    sends: list[Send] = []
    for item in resolved:
        if item["status"] == "ready":
            branch: ToolRequestState = {"id": item["id"], "request": item["request"]}
            sends.append(Send("tool_workflow", branch))

    return sends if sends else "collect"
