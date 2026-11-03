from typing import Literal

from langgraph.types import Send

from app.agent.state import AgentState, ToolRequestState


def route_after_params_check(
    state: ToolRequestState,
) -> Literal["integration", "missing_info", "fail"]:
    return state["next_step"]


def dispatch_requests(state: AgentState) -> list[Send] | str:
    # Dispatch each ready request independently
    sends = [
        Send(
            "tool_workflow",
            {
                "id": item["id"],
                "request": item["request"],
            },
        )
        for item in state["resolved_requests"]
        if item["status"] == "ready"
    ]

    return sends if sends else "collect"
