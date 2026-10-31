from typing import Annotated, Any

from langgraph.graph import MessagesState


def merge_parameters(
    old: dict[str, Any],
    new: dict[str, Any],
) -> dict[str, Any]:
    return {**old, **new}

class AgentState(MessagesState):
    parameters: Annotated[dict[str, Any], merge_parameters]
    requests: list[dict[str, Any]]
    entities: dict[str, Any]
    tool_results: dict[str, Any]
