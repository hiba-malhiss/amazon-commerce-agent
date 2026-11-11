from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.config import get_stream_writer


def emit_prompt(node: str, messages: list[BaseMessage]) -> None:
    prompt = "\n\n".join(
        str(message.content) for message in messages if isinstance(message, SystemMessage)
    )
    get_stream_writer()({"kind": "prompt", "node": node, "prompt": prompt})
