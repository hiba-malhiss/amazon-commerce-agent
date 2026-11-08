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
    referenced_entities: list[str]
    parameters: list[ExtractedParameterData]
    relation: Relation
    source_request_id: str | None


class ResolvedRequestData(TypedDict):
    question: str
    tool: str
    referenced_entities: list[str]  # references the user pointed at
    parameters: dict[str, ParameterValue]
    relation: Relation
    source_request_id: str | None


class ReadyRequest(TypedDict):
    id: str
    status: Literal["ready"]
    request: ResolvedRequestData
    result_references: NotRequired[list[str]]


class ClarificationRequest(TypedDict):
    id: str
    status: Literal["needs_clarification"]
    error: str


type ResolvedRequest = ReadyRequest | ClarificationRequest


class OutcomeResult(TypedDict):
    entities: list[MappedEntity]


class RequestOutcome(TypedDict):
    id: str
    status: Literal["success", "fail", "missing_info", "needs_clarification"]
    result: OutcomeResult | None
    missing_parameters: list[str]
    error: str | None
    status_code: NotRequired[int | None]  # HTTP status of the API call (set by api_call only)
