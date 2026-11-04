from app.agent.state import AgentStateUpdate, ToolRequestState
from app.agent.tool_graph import build_tool_graph

# Compile once, reuse for every request
tool_graph = build_tool_graph()


async def tool_workflow_node(
    state: ToolRequestState,
) -> AgentStateUpdate:

    # Execute the tool subgraph
    try:
        final = await tool_graph.ainvoke(state)

    except Exception:
        return {
            "outcomes": [
                {
                    "id": state["id"],
                    "status": "fail",
                    "result": None,
                    "missing_parameters": [],
                    "error": "Tool execution failed unexpectedly",
                }
            ]
        }

    # Read the outcome
    outcome = final.get("outcome")

    if outcome is None:
        outcome = {
            "id": state["id"],
            "status": "fail",
            "result": None,
            "missing_parameters": [],
            "error": "Tool workflow returned no outcome",
        }

    return {"outcomes": [outcome]}
