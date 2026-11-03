from langgraph.graph import END, START, StateGraph

from app.agent.nodes.understand import understand_node
from app.agent.state import AgentState


def build_graph(checkpointer):
    # Define the agent workflow
    graph = StateGraph(AgentState)

    # Register Nodes
    graph.add_node("understand", understand_node)
    graph.add_node("request_resolver", request_resolver_node)

    # Define execution order
    graph.add_edge(START, "understand")
    graph.add_edge("understand", "request_resolver")
    graph.add_edge("request_resolver", END)

    return graph.compile(checkpointer=checkpointer)
