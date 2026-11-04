from langgraph.config import get_stream_writer

from app.agent.state import ToolRequestState, ToolRequestUpdate


def missing_info_node(state: ToolRequestState) -> ToolRequestUpdate:
    writer = get_stream_writer()
    writer({"node": "missing_info", "status": "started", "data": {"request_id": state["id"]}})

    missing = state["missing_parameters"]

    writer(
        {
            "node": "missing_info",
            "status": "completed",
            "data": {"request_id": state["id"], "missing_parameters": missing},
        }
    )
    # Return the missing parameter outcome
    return {
        "outcome": {
            "id": state["id"],
            "status": "missing_info",
            "result": None,
            "missing_parameters": missing,
            "error": None,
        }
    }
