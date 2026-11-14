from langchain_core.messages import BaseMessage
from langgraph.config import get_stream_writer


def emit_prompt(node: str, messages: list[BaseMessage]) -> None:
    """Send the full LLM input (every message, labelled by role) for the Prompts panel."""
    prompt = "\n\n".join(f"[{message.type}]\n{message.content}" for message in messages)
    get_stream_writer()({"kind": "prompt", "node": node, "prompt": prompt})
