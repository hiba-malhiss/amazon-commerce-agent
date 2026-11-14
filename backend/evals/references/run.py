"""Evaluate references to visible results with LangSmith: Understanding picks, and code
(request_resolver) checks and corrects. Scores the product the agent would fetch.

    cd backend
    uv run python -m evals.references.run               # 3 runs per case
    uv run python -m evals.references.run --recreate    # after editing dataset.py
"""

import asyncio

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from app.agent.nodes.request_resolver import request_resolver_node
from app.agent.nodes.understand import understand_node
from app.agent.state import AgentState
from app.configurations.tools.registry import TOOLS_BY_CODE
from evals.common import run_experiment
from evals.references.dataset import DATASET_NAME, EXAMPLES

SEARCH_ID = "search"

# Understanding, then the code that checks its references and fills the product ids
graph = (
    StateGraph(AgentState)
    .add_node("understand", understand_node)
    .add_node("request_resolver", request_resolver_node)
    .add_edge(START, "understand")
    .add_edge("understand", "request_resolver")
    .add_edge("request_resolver", END)
    .compile()
)


async def resolve(inputs: dict) -> dict:
    """The case's search was the previous turn: its cards are visible, then the message."""
    entities = {
        f"product_{card['product_id']}": {
            "reference": f"product_{card['product_id']}",
            "position": number,
            "entity_code": "product",
            "attributes": card,
        }
        for number, card in enumerate(inputs["cards"], start=1)
    }
    history = [
        HumanMessage(text) if role == "human" else AIMessage(text)
        for role, text in inputs["history"]
    ]
    state = await graph.ainvoke(
        {
            "messages": [*history, HumanMessage(inputs["message"])],
            "entities": entities,
            "visible_entities": [
                {"items": [{"reference": ref, "request_id": SEARCH_ID} for ref in entities]}
            ],
            "recent_requests": [
                {
                    "id": SEARCH_ID,
                    "status": "ready",
                    "request": {
                        "question": inputs["history"][0][1],
                        "tool": "search_products",
                        "referenced_entities": [],
                        "parameters": {"product_name": "1TB SSD"},
                        "relation": "new",
                        "source_request_id": None,
                    },
                }
            ],
        }
    )
    resolved = state.get("resolved_requests", [])
    ready = [r["request"] for r in resolved if r["status"] == "ready"]
    return {
        "product_ids": [
            r["parameters"]["product_id"] for r in ready if "product_id" in r["parameters"]
        ],
        # The agent asks the user: a clarification, or a request missing a required
        # parameter (params_check turns it into missing_info)
        "clarification": any(r["status"] == "needs_clarification" for r in resolved)
        or any(missing_required(r) for r in ready),
    }


def missing_required(request: dict) -> bool:
    tool = TOOLS_BY_CODE.get(request["tool"])
    return bool(tool) and any(
        request["parameters"].get(p) is None for p in tool.required_parameters
    )


def reference(outputs: dict, reference_outputs: dict) -> dict:
    """The products the agent would fetch are the expected ones (any order), or it asks."""
    if reference_outputs.get("clarification"):
        return {"key": "reference", "score": outputs["clarification"]}
    return {
        "key": "reference",
        "score": not outputs["clarification"]
        and sorted(outputs["product_ids"]) == sorted(reference_outputs["product_ids"]),
    }


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(
        run_experiment(
            DATASET_NAME,
            "References to visible results, checked and corrected by code",
            EXAMPLES,
            resolve,
            [reference],
        )
    )
