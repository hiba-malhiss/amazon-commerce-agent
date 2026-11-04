from app.agent.state import ToolRequestState, ToolRequestUpdate


def fail_node(state: ToolRequestState) -> ToolRequestUpdate:
    # A step decided this request can't run (e.g. unknown tool)
    return {
        "outcome": {
            "id": state["id"],
            "status": "fail",
            "result": None,
            "missing_parameters": [],
            "error": state.get("error", "Request failed"),
        }
    }
