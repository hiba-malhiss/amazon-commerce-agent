from typing import Literal, NotRequired, TypedDict

from app.agent.schemas.execution import MappedEntity, ParameterValue

type Relation = Literal["new", "follow_up", "ambiguous"]


class ExtractedParameterData(TypedDict):
    code: str
    operation: Literal["set", "remove"]
    value: ParameterValue | None


class UnderstoodRequestData(TypedDict):
    question: str
    tool: str
    referenced_entities: list[str]  # visible results the user points at
    reference_quote: str | None  # the user's words that point at them
    parameters: list[ExtractedParameterData]
    relation: Relation
    source_request_id: str | None


class ResolvedRequestData(TypedDict):
    question: str
    tool: str
    referenced_entities: list[str]  # the entities the user pointed at
    parameters: dict[str, ParameterValue]
    relation: Relation
    source_request_id: str | None


class ReadyRequest(TypedDict):
    id: str
    status: Literal["ready"]
    request: ResolvedRequestData


class ClarificationRequest(TypedDict):
    id: str
    status: Literal["needs_clarification"]
    error: str


type ResolvedRequest = ReadyRequest | ClarificationRequest


class VisibleEntity(TypedDict):
    reference: str
    request_id: str  # the request whose result it is


class VisibleEntityList(TypedDict):
    """The cards one reply showed the user, card 1 first."""

    items: list[VisibleEntity]


class NumberedCard(TypedDict):
    """One result shown to the user as a numbered card this turn."""

    number: int
    request_id: str
    entity: MappedEntity


class OutcomeResult(TypedDict):
    entities: list[MappedEntity]


class RequestOutcome(TypedDict):
    id: str
    status: Literal["success", "fail", "missing_info", "needs_clarification"]
    result: OutcomeResult | None
    missing_parameters: list[str]
    error: str | None
    status_code: NotRequired[int | None]  # HTTP status of the API call (set by api_call only)
