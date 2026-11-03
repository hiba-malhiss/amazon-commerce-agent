from typing import Any

from langgraph.graph import MessagesState

from app.agent.schemas.resolution import (
    RequestHistoryEntry,
    ResolvedRequest,
)

# entities — Previously retrieved products.
# requests — Raw requests extracted by Understanding.
# resolved_requests — Requests after parameter merging.
# recent_requests — Saved requests with their resolved parameters for future follow-ups.
class AgentState(MessagesState):
    entities: dict[str, Any]
    requests: list[dict[str, Any]]
    resolved_requests: list[ResolvedRequest]
    recent_requests: list[RequestHistoryEntry]
