from app.agent.schemas.resolution import RequestOutcome
from app.agent.state import ToolRequestState
from app.agent.tool_graph import build_tool_graph

# Compile once, reuse for every request
tool_graph = build_tool_graph()


async def tool_workflow_node(
    state: ToolRequestState,
) -> dict[str, list[RequestOutcome]]:
    # Execute this request's tool workflow
    result = await tool_graph.ainvoke(state)

    # Send the outcome to the parent graph
    return {
        "outcomes": [result["outcome"]],
    }
