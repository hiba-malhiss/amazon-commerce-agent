from typing import Literal, TypedDict

from pydantic import JsonValue

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
