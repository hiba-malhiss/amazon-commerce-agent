from typing import Any

from app.configurations.integrations.registry import INTEGRATIONS_BY_CODE
from app.configurations.schemas import APIIntegrationConfig
from app.configurations.tools.registry import TOOLS_BY_CODE
from app.execution.entity_mapper import map_entities
from app.execution.integrations.api_executor import execute_api
from app.execution.parameter_validator import get_missing_parameters


async def execute_tool(
    tool_code: str,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    # Resolve tool configuration
    tool = TOOLS_BY_CODE.get(tool_code)

    if tool is None:
        raise ValueError(f"Unknown tool: {tool_code}")

    # Validate required parameters
    missing = get_missing_parameters(tool, parameters)

    if missing:
        return {
            "status": "missing_parameters",
            "tool_code": tool.code,
            "missing_parameters": missing,
        }

    # Resolve integration configuration
    integration = INTEGRATIONS_BY_CODE.get(tool.integration_code)

    if integration is None:
        raise ValueError(f"Unknown integration: {tool.integration_code}")

    # Execute the integration by type
    if isinstance(integration, APIIntegrationConfig):
        response = await execute_api(integration, parameters)

        entities = (
            map_entities(response, integration.entity_mapping)
            if integration.entity_mapping is not None
            else []
        )

        return {
            "status": "completed",
            "tool_code": tool.code,
            "tool_name": tool.name,
            "entities": entities,
            "data": response,
        }

    raise NotImplementedError(f"Unsupported integration type: {type(integration).__name__}")
