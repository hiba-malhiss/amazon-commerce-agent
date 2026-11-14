"""What every eval suite shares: upload its dataset once, then run it in LangSmith."""

import argparse
import os
from collections.abc import Awaitable, Callable

from langsmith import Client

from app.core.settings import settings


async def run_experiment(
    dataset_name: str,
    description: str,
    examples: list[dict],
    target: Callable[[dict], Awaitable[dict]],
    evaluators: list[Callable],
) -> None:
    """Run every example --repeats times (LLMs vary) and score it in LangSmith.

    --recreate re-uploads the dataset after its examples change.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=3, help="runs per case (LLMs vary)")
    parser.add_argument("--recreate", action="store_true", help="re-upload the dataset")
    args = parser.parse_args()

    if not os.environ.get("LANGSMITH_API_KEY"):
        raise SystemExit("LANGSMITH_API_KEY is not set: add it to backend/.env (not .env.example)")

    client = Client()
    if client.has_dataset(dataset_name=dataset_name) and args.recreate:
        client.delete_dataset(dataset_name=dataset_name)
    if not client.has_dataset(dataset_name=dataset_name):
        dataset = client.create_dataset(dataset_name, description=description)
        client.create_examples(dataset_id=dataset.id, examples=examples)

    await client.aevaluate(
        target,
        data=dataset_name,
        evaluators=evaluators,
        experiment_prefix=dataset_name,
        metadata={"model": settings.llm_model},
        num_repetitions=args.repeats,
        max_concurrency=4,
    )
