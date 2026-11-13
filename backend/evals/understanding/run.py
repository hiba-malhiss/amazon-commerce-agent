"""Evaluate one-turn Understanding with LangSmith.

    cd backend
    uv run python -m evals.understanding.run               # 3 runs per case
    uv run python -m evals.understanding.run --repeats 1
    uv run python -m evals.understanding.run --recreate    # re-upload the dataset

Needs LANGSMITH_API_KEY (and OPENAI_API_KEY) in the environment or backend/.env.
Results appear in LangSmith under Datasets → understanding-one-turn → Experiments,
with one score per field, so a failure shows which part was wrong.
"""

import argparse
import asyncio
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langsmith import Client

from app.agent.nodes.understand import understand_node
from app.agent.state import AgentState
from app.core.settings import settings
from evals.understanding.dataset import DATASET_NAME, EXAMPLES

# The real Understanding node, alone: run inside a graph so its event writer works
graph = (
    StateGraph(AgentState)
    .add_node("understand", understand_node)
    .add_edge(START, "understand")
    .add_edge("understand", END)
    .compile()
)


async def understand(inputs: dict) -> dict:
    """One turn: the message alone, with no earlier requests or visible results."""
    state = await graph.ainvoke(
        {
            "messages": [HumanMessage(inputs["message"])],
            "recent_requests": [],
            "visible_entities": [],
            "entities": {},
        }
    )
    return {
        "requests": [
            {
                "tool": request["tool"],
                "parameters": {
                    p["code"]: p["value"] for p in request["parameters"] if p["operation"] == "set"
                },
            }
            for request in state.get("requests", [])
        ],
        "out_of_scope": state.get("out_of_scope", False),
    }


# --- Evaluators: one score per field ---------------------------------------------


def request_count(outputs: dict, reference_outputs: dict) -> dict:
    return {
        "key": "request_count",
        "score": len(outputs["requests"]) == len(reference_outputs["requests"]),
    }


def tools(outputs: dict, reference_outputs: dict) -> dict:
    return {
        "key": "tools",
        "score": [r["tool"] for r in outputs["requests"]]
        == [r["tool"] for r in reference_outputs["requests"]],
    }


def parameters(outputs: dict, reference_outputs: dict) -> dict:
    """Share of expected parameters present with the right value, request by request."""
    expected = reference_outputs["requests"]
    if not expected:
        return {"key": "parameters", "score": 1.0}
    if len(outputs["requests"]) != len(expected):
        return {"key": "parameters", "score": 0.0}

    checks = [
        value_matches(want, got["parameters"].get(code))
        for want_request, got in zip(expected, outputs["requests"], strict=True)
        for code, want in (want_request["parameters"] or {}).items()
    ]
    return {"key": "parameters", "score": sum(checks) / len(checks) if checks else 1.0}


def out_of_scope(outputs: dict, reference_outputs: dict) -> dict:
    return {
        "key": "out_of_scope",
        "score": outputs["out_of_scope"] == reference_outputs["out_of_scope"],
    }


def correct(outputs: dict, reference_outputs: dict) -> dict:
    """The whole case right: every field above."""
    scores = [
        check(outputs, reference_outputs)["score"]
        for check in (request_count, tools, parameters, out_of_scope)
    ]
    return {"key": "correct", "score": all(score == 1 for score in scores)}


def value_matches(want, got) -> bool:
    """Text: contained, case insensitive ("headphones" in "wireless headphones").
    Numbers: equal ("100" counts as 100)."""
    if isinstance(want, str):
        return isinstance(got, str) and want.lower() in got.lower()
    try:
        return float(got) == float(want)
    except (TypeError, ValueError):
        return False


# --- Run ---------------------------------------------------------------------------


def sync_dataset(client: Client, recreate: bool) -> None:
    """Upload the cases once; --recreate replaces them after the cases change."""
    if client.has_dataset(dataset_name=DATASET_NAME):
        if not recreate:
            return
        client.delete_dataset(dataset_name=DATASET_NAME)
    dataset = client.create_dataset(
        DATASET_NAME, description="Understanding, one user message with no earlier turns"
    )
    client.create_examples(dataset_id=dataset.id, examples=EXAMPLES)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=3, help="runs per case (LLMs vary)")
    parser.add_argument("--recreate", action="store_true", help="re-upload the dataset")
    args = parser.parse_args()

    if not os.environ.get("LANGSMITH_API_KEY"):
        raise SystemExit("LANGSMITH_API_KEY is not set: add it to backend/.env (not .env.example)")

    client = Client()
    sync_dataset(client, args.recreate)
    await client.aevaluate(
        understand,
        data=DATASET_NAME,
        evaluators=[request_count, tools, parameters, out_of_scope, correct],
        experiment_prefix="understanding-one-turn",
        metadata={"model": settings.llm_model},
        num_repetitions=args.repeats,
        max_concurrency=4,
    )


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
