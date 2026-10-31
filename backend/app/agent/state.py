from typing import Any

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    parameters: dict[str, Any]
    requests: list[dict[str, Any]]
    entities: dict[str, Any]
    tool_results: dict[str, Any]
