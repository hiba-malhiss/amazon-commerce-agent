from langgraph.graph import END, START, StateGraph

from app.agent.nodes.integration import integration_node
from app.agent.nodes.missing_info import missing_info_node
from app.agent.nodes.params_check import params_check_node
from app.agent.routing import route_after_params_check
from app.agent.state import ToolRequestState


def build_tool_graph():
    graph = StateGraph(ToolRequestState)

    # Register nodes
    graph.add_node("params_check", params_check_node)
    graph.add_node("integration", integration_node)
    graph.add_node("missing_info", missing_info_node)

    graph.add_edge(START, "params_check")
    # Route based on parameter validation
    graph.add_conditional_edges(
        "params_check",
        route_after_params_check,
        {
            "integration": "integration",
            "missing_info": "missing_info",
        },
    )

    graph.add_edge("integration", END)
    graph.add_edge("missing_info", END)

    return graph.compile()
