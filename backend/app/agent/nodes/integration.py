import httpx

from app.agent.schemas.resolution import RequestOutcome
from app.agent.state import ToolRequestState
from app.configurations.integrations.registry import INTEGRATIONS_BY_CODE
from app.configurations.schemas import APIIntegrationConfig
from app.configurations.tools.registry import TOOLS_BY_CODE
from app.execution.entity_mapper import map_entities
from app.execution.integrations.api_executor import execute_api
from app.execution.schemas import ToolResult, ToolResultStatus


async def integration_node(
    state: ToolRequestState,
) -> dict[str, RequestOutcome]:
    request = state["request"]

    # Resolve integration configuration
    tool = TOOLS_BY_CODE.get(request["tool"])
    integration = INTEGRATIONS_BY_CODE.get(tool.integration_code) if tool else None

    try:
        if not isinstance(integration, APIIntegrationConfig):
            raise ValueError("Unknown or unsupported integration")

        # Execute integration
        response = await execute_api(
            integration,
            request["parameters"],
        )

        # Map entities when configured
        entities = (
            map_entities(response, integration.entity_mapping)
            if integration.entity_mapping is not None
            else []
        )

        result = ToolResult(
            status=ToolResultStatus.COMPLETED,
            data={"entities": entities},
        )

    except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
        result = ToolResult(
            status=ToolResultStatus.FAILED,
            error=str(exc),
        )

    # Return the request's final outcome
    return {
        "outcome": {
            "id": state["id"],
            "status": ("success" if result.status == ToolResultStatus.COMPLETED else "fail"),
            "result": (
                result.model_dump(mode="json")["data"]
                if result.status == ToolResultStatus.COMPLETED
                else None
            ),
            "missing_parameters": [],
            "error": result.error,
        }
    }
