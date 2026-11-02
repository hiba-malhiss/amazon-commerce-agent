from typing import Any

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    active_request: dict[str, Any] | None
    entities: dict[str, Any]
    requests: list[dict[str, Any]]
