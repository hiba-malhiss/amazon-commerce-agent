from langgraph.config import get_stream_writer

from app.agent.state import ToolRequestState, ToolRequestUpdate
from app.configurations.tools.registry import TOOLS_BY_CODE


def params_check_node(state: ToolRequestState) -> ToolRequestUpdate:
    writer = get_stream_writer()
    writer({"node": "params_check", "status": "started", "data": {"request_id": state["id"]}})

    # Get the current request
    request = state["request"]
    tool = TOOLS_BY_CODE.get(request["tool"])

    if tool is None:
        error = f"Unknown tool: {request['tool']}"
        writer(
            {
                "node": "params_check",
                "status": "failed",
                "data": {"request_id": state["id"], "error": error, "tool": request["tool"]},
            }
        )
        return {
            "next_step": "fail",
            "outcome": {
                "id": state["id"],
                "status": "fail",
                "result": None,
                "missing_parameters": [],
                "error": error,
            },
        }

    # Find required parameters with missing values
    missing = [code for code in tool.required_parameters if request["parameters"].get(code) is None]
    next_step = "missing_info" if missing else "api_call"

    # Parameter values are omitted; the api_call event shows what is sent
    writer(
        {
            "node": "params_check",
            "status": "completed",
            "data": {
                "request_id": state["id"],
                "next_step": next_step,
                "tool": request["tool"],
                "missing_parameters": missing,
            },
        }
    )
    return {"missing_parameters": missing, "next_step": next_step}
