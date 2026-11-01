import os
from typing import Any

import httpx
from dotenv import load_dotenv

from app.configurations.schemas import APIIntegrationConfig, AuthenticationConfig
from app.execution.integrations.request_builder import build_api_request

load_dotenv()


def get_required_env(name: str | None) -> str:
    # Resolve credentials without storing secrets in config
    if not name or not (value := os.getenv(name)):
        raise ValueError(f"Missing credential: {name}")
    return value


def resolve_auth(
    config: AuthenticationConfig,
) -> tuple[dict[str, str], dict[str, str], httpx.BasicAuth | None]:
    headers = {}
    query_params = {}
    auth = None

    if config.type == "api_key":
        key = get_required_env(config.api_key_env)
        value = f"{config.key_prefix}{key}"

        if not config.key_name:
            raise ValueError("API key name is required")

        if config.key_location == "header":
            headers[config.key_name] = value
        else:
            query_params[config.key_name] = value

    elif config.type == "basic":
        auth = httpx.BasicAuth(
            username=get_required_env(config.username_env),
            password=get_required_env(config.password_env),
        )

    return headers, query_params, auth


async def execute_api(
    integration: APIIntegrationConfig,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    # Build the configured API request
    request = build_api_request(integration, parameters)

    auth_headers, auth_query, basic_auth = resolve_auth(integration.authentication)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=request["method"],
            url=request["url"],
            headers={**request["headers"], **auth_headers},
            params={**request["query_params"], **auth_query},
            json=request["payload"] or None,
            auth=basic_auth,
        )

        response.raise_for_status()
        return response.json()
