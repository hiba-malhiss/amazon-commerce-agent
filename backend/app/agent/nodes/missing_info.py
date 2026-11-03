from app.agent.state import ToolRequestState


def missing_info_node(state: ToolRequestState) -> dict:
    # Missing parameters were identified by PARAMS_CHECK
    return {
        "outcome": "missing_info",
    }
