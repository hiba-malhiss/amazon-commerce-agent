from typing import Literal

from app.agent.state import ToolRequestState


def route_after_params_check(
    state: ToolRequestState,
) -> Literal["integration", "missing_info", "fail"]:
    return state["next_step"]
