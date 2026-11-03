from typing import Literal, TypedDict

type ParameterValue = str | int | float | bool


class ResolvedRequestData(TypedDict):
    question: str
    tool: str
    entities: list[str]
    parameters: dict[str, ParameterValue]
    relation: Literal["new", "follow_up", "ambiguous"]
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


class RequestHistoryEntry(TypedDict):
    id: str
    question: str
    tool: str
    parameters: dict[str, ParameterValue]
    entities: list[str]
    status: Literal["ready"]


class RequestOutcome(TypedDict):
    id: str
    status: Literal["success", "fail", "missing_info"]
    result: dict[str, object] | None
    missing_parameters: list[str]
    error: str | None
