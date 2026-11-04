import operator
from typing import Annotated, Literal, NotRequired, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import MessagesState
from langgraph.types import Overwrite

from app.agent.schemas.resolution import (
    ReadyRequest,
    RequestOutcome,
    ResolvedRequest,
    ResolvedRequestData,
    UnderstoodRequestData,
)
from app.execution.schemas import MappedEntity


class AgentState(MessagesState):
    # Persistent across messages
    entities: dict[str, MappedEntity]  # previously retrieved products, by reference
    recent_requests: list[ReadyRequest]  # resolved requests, for follow-ups

    # Current message only (reset by `understand`)
    requests: list[UnderstoodRequestData]  # raw requests from Understanding
    resolved_requests: list[ResolvedRequest]  # after parameter merging
    outcomes: Annotated[list[RequestOutcome], operator.add]  # one per parallel branch
    collected_outcomes: list[RequestOutcome]  # outcomes in request order
    reply: str | None


class AgentStateUpdate(TypedDict, total=False):
    """What any main-graph node may return: a partial AgentState."""

    messages: list[AnyMessage]
    entities: dict[str, MappedEntity]
    recent_requests: list[ReadyRequest]
    requests: list[UnderstoodRequestData]
    resolved_requests: list[ResolvedRequest]
    # list → appended (operator.add); Overwrite → replaced, used to reset each message
    outcomes: list[RequestOutcome] | Overwrite
    collected_outcomes: list[RequestOutcome]
    reply: str | None


type ToolStep = Literal["integration", "missing_info", "fail"]


class ToolRequestState(TypedDict):
    id: str
    request: ResolvedRequestData
    missing_parameters: NotRequired[list[str]]
    next_step: NotRequired[ToolStep]
    error: NotRequired[str]
    outcome: NotRequired[RequestOutcome]


class ToolRequestUpdate(TypedDict, total=False):
    """What any tool-workflow node may return: a partial ToolRequestState."""

    missing_parameters: list[str]
    next_step: ToolStep
    error: str
    outcome: RequestOutcome
