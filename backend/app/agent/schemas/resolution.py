from typing import Literal, TypedDict

from app.execution.schemas import MappedEntity, ParameterValue

type Relation = Literal["new", "follow_up", "ambiguous"]


class ExtractedParameterData(TypedDict):
    code: str
    operation: Literal["set", "remove"]
    value: ParameterValue | None


class UnderstoodRequestData(TypedDict):
    question: str
    tool: str
    entities: list[str]
    parameters: list[ExtractedParameterData]
    relation: Relation
    source_request_id: str | None


class ReadyRequest(TypedDict):
    id: str
    status: Literal["ready"]
    request: UnderstoodRequestData


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
