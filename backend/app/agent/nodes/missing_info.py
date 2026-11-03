from app.agent.schemas.resolution import RequestOutcome
from app.agent.state import ToolRequestState


def missing_info_node(
    state: ToolRequestState,
) -> dict[str, RequestOutcome]:
    # Return the missing parameter outcome
    return {
        "outcome": {
            "id": state["id"],
            "status": "missing_info",
            "result": None,
            "missing_parameters": state["missing_parameters"],
            "error": None,
        }
    }
