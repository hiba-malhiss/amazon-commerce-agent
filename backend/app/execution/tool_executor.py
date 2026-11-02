from typing import Any

import httpx

from app.configurations.integrations.registry import INTEGRATIONS_BY_CODE
from app.configurations.schemas import APIIntegrationConfig
from app.configurations.tools.registry import TOOLS_BY_CODE
from app.execution.entity_mapper import map_entities
from app.execution.integrations.api_executor import execute_api
from app.execution.parameter_validator import get_missing_parameters
from app.execution.schemas import ToolResult, ToolResultStatus


async def execute_tool(
    tool_code: str,
    parameters: dict[str, Any],
) -> ToolResult:
    # Resolve tool configuration
    tool = TOOLS_BY_CODE.get(tool_code)

    if tool is None:
        return ToolResult(
            status=ToolResultStatus.FAILED,
            error=f"Unknown tool: {tool_code}",
        )

    # Validate required parameters
    missing = get_missing_parameters(tool, parameters)

    if missing:
        return ToolResult(
            status=ToolResultStatus.MISSING_PARAMETERS,
            missing_parameters=missing,
        )

    # Resolve integration configuration
    integration = INTEGRATIONS_BY_CODE.get(tool.integration_code)

    if integration is None:
        return ToolResult(
            status=ToolResultStatus.FAILED,
            error=f"Unknown integration: {tool.integration_code}",
        )

    # Execute integration and map its response
    try:
        if isinstance(integration, APIIntegrationConfig):
            response = await execute_api(integration, parameters)

            entities = (
                map_entities(response, integration.entity_mapping)
                if integration.entity_mapping is not None
                else []
            )

            return ToolResult(
                status=ToolResultStatus.COMPLETED,
                data={"entities": entities},
            )

        return ToolResult(
            status=ToolResultStatus.FAILED,
            error=f"Unsupported integration type: {type(integration).__name__}",
        )

    except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
        # Return execution errors without crashing the graph
        return ToolResult(
            status=ToolResultStatus.FAILED,
            error=str(exc),
        )
