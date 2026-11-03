import operator
from typing import Annotated, Any, Literal, NotRequired, TypedDict

from langgraph.graph import MessagesState

from app.agent.schemas.resolution import (
    RequestHistoryEntry,
    RequestOutcome,
    ResolvedRequest,
    ResolvedRequestData,
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
    outcomes: Annotated[list[RequestOutcome], operator.add]


class ToolRequestState(TypedDict):
    id: str
    request: ResolvedRequestData
    missing_parameters: NotRequired[list[str]]
    result: NotRequired[dict[str, object]]
    next_step: NotRequired[Literal["integration", "missing_info", "success", "fail"]]
    error: NotRequired[str]
    outcome: NotRequired[RequestOutcome]
