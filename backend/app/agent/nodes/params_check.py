from app.agent.state import ToolRequestState
from app.configurations.tools.registry import TOOLS_BY_CODE
from app.execution.parameter_validator import get_missing_parameters


def params_check_node(state: ToolRequestState) -> dict:
    # Get the current request
    request = state["request"]
    tool = TOOLS_BY_CODE.get(request["tool"])

    if tool is None:
        return {
            "next_step": "fail",
            "error": f"Unknown tool: {request['tool']}",
        }

    # Validate required parameters
    missing = get_missing_parameters(
        tool,
        request["parameters"],
    )

    # Select the next workflow step
    return {
        "missing_parameters": missing,
        "next_step": "missing_info" if missing else "integration",
    }
