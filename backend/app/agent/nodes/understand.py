from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.prompts.understanding import UNDERSTANDING_PROMPT
from app.agent.schemas.understanding import UnderstandingResult
from app.agent.state import AgentState
from app.configurations.parameters import PARAMETERS
from app.configurations.tools.registry import TOOLS
from app.llm.client import llm_client


async def understand_node(state: AgentState) -> dict[str, Any]:
    # Load configurations
    parameters = [p.model_dump() for p in PARAMETERS]

    tools = [
        {
            "code": t.code,
            "name": t.name,
            "description": t.description,
        }
        for t in TOOLS
    ]

    # Read previous request summaries and known entities - from the prev message
    previous_requests = state.get("recent_requests") or []
    known_entities = state.get("entities") or {}

    # Get only the latest user message
    last_user_message = state["messages"][-1]

    if not isinstance(last_user_message, HumanMessage):
        raise ValueError("Latest message must be a user message")

    # Build Understanding context
    system_message = SystemMessage(
        content=UNDERSTANDING_PROMPT.format(
            parameters=parameters,
            tools=tools,
            recent_requests=previous_requests[-8:],
            known_entities=list(known_entities.values()),
        )
    )

    # Extract requests without executing or merging parameters
    result = await llm_client.structured_completion(
        messages=[system_message, last_user_message],
        response_schema=UnderstandingResult,
    )

    if not isinstance(result, UnderstandingResult):
        raise ValueError("Invalid understanding result")

    return {
        "requests": [request.model_dump() for request in result.requests],
    }
