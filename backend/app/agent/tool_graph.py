from langgraph.graph import END, START, StateGraph

from app.agent.nodes.api_call import api_call_node
from app.agent.nodes.missing_info import missing_info_node
from app.agent.nodes.params_check import params_check_node
from app.agent.routing import route_after_params_check
from app.agent.state import ToolRequestState


def build_tool_graph():
    graph = StateGraph(ToolRequestState)

    # Register nodes
    graph.add_node("params_check", params_check_node)
    graph.add_node("api_call", api_call_node)
    graph.add_node("missing_info", missing_info_node)

    graph.add_edge(START, "params_check")
    # Route based on parameter validation ("fail" = unknown tool, outcome already set)
    graph.add_conditional_edges(
        "params_check",
        route_after_params_check,
        {
            "api_call": "api_call",
            "missing_info": "missing_info",
            "fail": END,
        },
    )
    graph.add_edge("api_call", END)
    graph.add_edge("missing_info", END)

    return graph.compile()
