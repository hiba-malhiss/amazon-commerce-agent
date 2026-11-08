import os
import time
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from langgraph.config import get_stream_writer
from pydantic import JsonValue

from app.agent.schemas.execution import ApiRequest, MappedEntity, ParameterValue
from app.agent.state import ToolRequestState, ToolRequestUpdate
from app.configurations.entities.registry import ENTITIES_BY_CODE
from app.configurations.integrations.registry import INTEGRATIONS_BY_CODE
from app.configurations.schemas import (
    APIIntegrationConfig,
    AuthenticationConfig,
    EntityMappingConfig,
)
from app.configurations.tools.registry import TOOLS_BY_CODE

load_dotenv()


async def api_call_node(state: ToolRequestState) -> ToolRequestUpdate:
    writer = get_stream_writer()
    request = state["request"]

    # Resolve the integration configured for this tool
    tool = TOOLS_BY_CODE.get(request["tool"])
    integration = (
        INTEGRATIONS_BY_CODE.get(tool.integration_code) if tool and tool.integration_code else None
    )
    if not isinstance(integration, APIIntegrationConfig):
        return failed(state, writer, "Unknown or unsupported integration")

    api_request = build_request(integration, request["parameters"])

    # Emit what the UI needs to show the call. Omitted: headers and credentials
    # (auth is added after this point), and the response body (can be large)
    writer(
        {
            "node": "api_call",
            "status": "started",
            "data": {
                "request_id": state["id"],
                "integration": integration.code,
                "method": api_request["method"],
                "url": api_request["url"],
                "query_params": api_request["query_params"],
                "payload": api_request["payload"],
            },
        }
    )

    started = time.perf_counter()
    status_code: int | None = None
    try:
        auth_headers, auth_query, basic_auth = resolve_auth(integration.authentication)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=api_request["method"],
                url=api_request["url"],
                headers={**api_request["headers"], **auth_headers},
                params={**api_request["query_params"], **auth_query},
                json=api_request["payload"] or None,
                auth=basic_auth,
            )
        status_code = response.status_code
        response.raise_for_status()
        body: JsonValue = response.json()

        # Integrations must return a JSON object; anything else is a failed call
        if not isinstance(body, dict):
            raise TypeError(f"Expected a JSON object, got {type(body).__name__}")

        # Process the response into entities (none when the integration maps none)
        entities = map_entities(body, integration.entity_mapping)

    except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
        return failed(state, writer, str(exc), status_code, elapsed_ms(started))

    writer(
        {
            "node": "api_call",
            "status": "completed",
            "data": {
                "request_id": state["id"],
                "status_code": status_code,
                "duration_ms": elapsed_ms(started),
                "entities": entities if integration.entity_mapping is not None else None,
            },
        }
    )
    return {
        "outcome": {
            "id": state["id"],
            "status": "success",
            "result": {"entities": entities},
            "missing_parameters": [],
            "error": None,
            "status_code": status_code,
        }
    }


def failed(
    state: ToolRequestState,
    writer,
    error: str,
    status_code: int | None = None,
    duration_ms: int | None = None,
) -> ToolRequestUpdate:
    writer(
        {
            "node": "api_call",
            "status": "failed",
            "data": {
                "request_id": state["id"],
                "status_code": status_code,
                "duration_ms": duration_ms,
                "error": error,
            },
        }
    )
    # A failed call is the request's final outcome
    return {
        "outcome": {
            "id": state["id"],
            "status": "fail",
            "result": None,
            "missing_parameters": [],
            "error": error,
            # None when no response came back (network error, timeout, missing credential)
            "status_code": status_code,
        }
    }


def build_request(
    integration: APIIntegrationConfig,
    parameters: dict[str, ParameterValue],
) -> ApiRequest:
    # Map API field names to the resolved parameter values
    def resolve(mapping: dict[str, str]) -> dict[str, ParameterValue]:
        return {
            api_field: parameters[parameter_code]
            for api_field, parameter_code in mapping.items()
            if parameters.get(parameter_code) is not None
        }

    return {
        "url": integration.url,
        "method": integration.method,
        "headers": integration.headers,
        "query_params": {**integration.static_query_params, **resolve(integration.query_params)},
        "payload": resolve(integration.payload),
    }


def resolve_auth(
    config: AuthenticationConfig,
) -> tuple[dict[str, str], dict[str, str], httpx.BasicAuth | None]:
    # Credentials come from env vars, never from config or the trace
    def env(name: str | None) -> str:
        if not name or not (value := os.getenv(name)):
            raise ValueError(f"Missing credential: {name}")
        return value

    headers: dict[str, str] = {}
    query_params: dict[str, str] = {}
    auth = None

    if config.type == "api_key":
        if not config.key_name:
            raise ValueError("API key name is required")
        value = f"{config.key_prefix}{env(config.api_key_env)}"
        if config.key_location == "header":
            headers[config.key_name] = value
        else:
            query_params[config.key_name] = value

    elif config.type == "basic":
        auth = httpx.BasicAuth(username=env(config.username_env), password=env(config.password_env))

    return headers, query_params, auth


def map_entities(
    response: dict[str, JsonValue],
    mapping: EntityMappingConfig | None,
) -> list[MappedEntity]:
    # Not every integration returns entities: no mapping, nothing to map
    if mapping is None:
        return []

    entity_config = ENTITIES_BY_CODE[mapping.entity_code]
    items = get_path(response, mapping.collection_path)
    if isinstance(items, dict):
        items = [items]  # a details endpoint returns one object, not a list

    entities: list[MappedEntity] = []
    for index, item in enumerate(items if isinstance(items, list) else []):
        if not isinstance(item, dict):
            continue

        # Map API fields to entity parameters
        attributes = {code: get_path(item, path) for code, path in mapping.field_mapping.items()}

        # Use the configured identifier when available
        identifier = (
            attributes.get(entity_config.identifier_parameter)
            if entity_config.identifier_parameter
            else None
        )
        if identifier is None or identifier == "" or isinstance(identifier, (list, dict)):
            identifier = uuid4().hex

        entities.append(
            {
                "reference": f"{entity_config.code}_{identifier}",
                "position": index + 1,
                "entity_code": entity_config.code,
                "attributes": attributes,
            }
        )
    return entities


def get_path(data: JsonValue, path: str) -> JsonValue:
    # Read a nested field like "product.price.value"
    value = data
    for key in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def elapsed_ms(started: float) -> int:
    return round((time.perf_counter() - started) * 1000)
