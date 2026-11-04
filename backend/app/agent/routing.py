from langgraph.types import Send

from app.agent.state import AgentState, ToolRequestState, ToolStep


def route_after_params_check(state: ToolRequestState) -> ToolStep:
    return state.get("next_step", "fail")


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
