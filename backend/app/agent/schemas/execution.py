from enum import StrEnum
from typing import Literal, TypedDict

from pydantic import BaseModel, Field, JsonValue

# A parameter value as extracted from the user and sent to integrations
type ParameterValue = str | int | float | bool

type HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


class ApiRequest(TypedDict):
    """An HTTP request built from an APIIntegrationConfig and resolved parameters."""

    url: str
    method: HttpMethod
    headers: dict[str, str]
    query_params: dict[str, ParameterValue]
    payload: dict[str, ParameterValue]


class MappedEntity(TypedDict):
    """One item from an integration response, mapped by EntityMappingConfig."""

    reference: str  # e.g. "product_B0CHR9K2LM"
    position: int  # 1-based position in the response
    entity_code: str  # e.g. "product"
    attributes: dict[str, JsonValue]  # entity parameter code → value from the API


class ToolResultStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    MISSING_PARAMETERS = "missing_parameters"


class ToolResultData(BaseModel):
    entities: list[MappedEntity] = Field(default_factory=list)


class ToolResult(BaseModel):
    # Errors are results, not exceptions, so one failed tool never breaks the graph
    status: ToolResultStatus
    data: ToolResultData = Field(default_factory=ToolResultData)
    error: str | None = None
    missing_parameters: list[str] = Field(default_factory=list)
