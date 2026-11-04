from langgraph.graph import END, START, StateGraph

from app.agent.nodes.collect import collect_node
from app.agent.nodes.request_resolver import request_resolver_node
from app.agent.nodes.respond import respond_node
from app.agent.nodes.tool_workflow import tool_workflow_node
from app.agent.nodes.understand import understand_node
from app.agent.routing import dispatch_requests
from app.agent.state import AgentState


def build_graph(checkpointer):
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("understand", understand_node)
    graph.add_node("request_resolver", request_resolver_node)
    graph.add_node("tool_workflow", tool_workflow_node)
    graph.add_node("collect", collect_node)
    graph.add_node("respond", respond_node)

    # Understand and resolve requests
    graph.add_edge(START, "understand")
    graph.add_conditional_edges(
        "understand",
        lambda state: (
            "respond"
            if any(
                outcome["id"] == "understand" and outcome["status"] == "fail"
                for outcome in state.get("collected_outcomes", [])
            )
            else "request_resolver"
        ),
        {
            "respond": "respond",
            "request_resolver": "request_resolver",
        },
    )

    # Dispatch requests in parallel
    graph.add_conditional_edges(
        "request_resolver",
        dispatch_requests,
        ["tool_workflow", "collect"],
    )

    # Combine results and generate response
    graph.add_edge("tool_workflow", "collect")
    graph.add_edge("collect", "respond")
    graph.add_edge("respond", END)

    return graph.compile(checkpointer=checkpointer)
