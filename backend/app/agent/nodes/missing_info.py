from app.agent.state import ToolRequestState, ToolRequestUpdate


def missing_info_node(state: ToolRequestState) -> ToolRequestUpdate:
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
