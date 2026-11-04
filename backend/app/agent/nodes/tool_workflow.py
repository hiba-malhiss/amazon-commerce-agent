from langgraph.config import get_stream_writer

from app.agent.schemas.resolution import RequestOutcome
from app.agent.state import AgentStateUpdate, ToolRequestState
from app.agent.tool_graph import build_tool_graph

# Compile once, reuse for every request
tool_graph = build_tool_graph()


async def tool_workflow_node(
    state: ToolRequestState,
) -> AgentStateUpdate:
    writer = get_stream_writer()
    writer(
        {
            "node": "tool_workflow",
            "status": "started",
            "data": {"request_id": state["id"], "tool": state["request"]["tool"]},
        }
    )

    # Execute the tool subgraph (its nodes emit their own events)
    try:
        final = await tool_graph.ainvoke(state)
        outcome: RequestOutcome | None = final.get("outcome")
        if outcome is None:
            raise RuntimeError("Tool workflow returned no outcome")

    except Exception as exc:
        error = "Tool execution failed unexpectedly"
        writer(
            {
                "node": "tool_workflow",
                "status": "failed",
                "data": {"request_id": state["id"], "error": f"{error}: {exc}"},
            }
        )
        outcome = {
            "id": state["id"],
            "status": "fail",
            "result": None,
            "missing_parameters": [],
            "error": error,
        }
        return {"outcomes": [outcome]}

    writer(
        {
            "node": "tool_workflow",
            "status": "completed",
            "data": {"request_id": state["id"], "outcome": outcome["status"]},
        }
    )
    return {"outcomes": [outcome]}
