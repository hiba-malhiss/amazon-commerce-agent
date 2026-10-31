from typing import Any

from app.schemas.config import APIIntegrationConfig


def build_api_request(
    integration: APIIntegrationConfig,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    # Map API field names to extracted parameter values
    def resolve(mapping: dict[str, str]) -> dict[str, Any]:
        return {
            api_field: parameters[parameter_code]
            for api_field, parameter_code in mapping.items()
            if parameters.get(parameter_code) is not None
        }

    return {
        "url": integration.url,
        "method": integration.method,
        "headers": integration.headers,
        "query_params": {
            **integration.static_query_params,
            **resolve(integration.query_params),
        },
        "payload": resolve(integration.payload),
    }
