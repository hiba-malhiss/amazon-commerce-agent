from langgraph.graph import END, START, StateGraph

from app.agent.nodes.understand import understand_node
from app.agent.state import AgentState


def build_graph(checkpointer):
    # Define the agent workflow
    graph = StateGraph(AgentState)

    # Register Nodes
    graph.add_node("understand", understand_node)

    # Define execution order
    graph.add_edge(START, "understand")
    graph.add_edge("understand", END)

    return graph.compile(checkpointer=checkpointer)
