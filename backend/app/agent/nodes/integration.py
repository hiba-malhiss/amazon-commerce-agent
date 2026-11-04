import httpx

from app.agent.state import ToolRequestState, ToolRequestUpdate
from app.configurations.integrations.registry import INTEGRATIONS_BY_CODE
from app.configurations.schemas import APIIntegrationConfig
from app.configurations.tools.registry import TOOLS_BY_CODE
from app.execution.entity_mapper import map_entities
from app.execution.integrations.api_executor import execute_api
from app.execution.schemas import ToolResult, ToolResultData, ToolResultStatus


async def integration_node(state: ToolRequestState) -> ToolRequestUpdate:
    request = state["request"]

    # Resolve integration configuration
    tool = TOOLS_BY_CODE.get(request["tool"])
    integration = (
        INTEGRATIONS_BY_CODE.get(tool.integration_code) if tool and tool.integration_code else None
    )

    try:
        if not isinstance(integration, APIIntegrationConfig):
            raise ValueError("Unknown or unsupported integration")

        # Execute integration
        response = await execute_api(integration, request["parameters"])

        # Map entities when configured
        entities = (
            map_entities(response, integration.entity_mapping)
            if integration.entity_mapping is not None
            else []
        )

        result = ToolResult(
            status=ToolResultStatus.COMPLETED,
            data=ToolResultData(entities=entities),
        )

    except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
        result = ToolResult(status=ToolResultStatus.FAILED, error=str(exc))

    succeeded = result.status == ToolResultStatus.COMPLETED

    # Return the request's final outcome
    return {
        "outcome": {
            "id": state["id"],
            "status": "success" if succeeded else "fail",
            "result": {"entities": result.data.entities} if succeeded else None,
            "missing_parameters": [],
            "error": result.error,
        }
    }
