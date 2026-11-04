from app.agent.state import AgentStateUpdate, ToolRequestState
from app.agent.tool_graph import build_tool_graph

# Compile once, reuse for every request
tool_graph = build_tool_graph()


async def tool_workflow_node(state: ToolRequestState) -> AgentStateUpdate:
    # Execute this request's tool workflow
    final = await tool_graph.ainvoke(state)

    # Every path through the subgraph ends in a node that sets `outcome`
    outcome = final.get("outcome")
    if outcome is None:
        raise ValueError(f"Tool workflow ended without an outcome for {state['id']}")

    # Send the outcome to the parent graph
    return {"outcomes": [outcome]}
