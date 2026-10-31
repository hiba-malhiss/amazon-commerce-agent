from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.prompts.understanding import UNDERSTANDING_PROMPT
from app.agent.state import AgentState
from app.config.parameters import PARAMETERS
from app.config.tools.registry import TOOLS
from app.llm.client import llm_client
from app.schemas.understanding import UnderstandingResult


async def understand_node(state: AgentState) -> dict[str, Any]:
    # Load parameter and tool configurations
    parameters = [p.model_dump() for p in PARAMETERS]

    tools = [
        {
            "code": t.code,
            "name": t.name,
            "description": t.description,
        }
        for t in TOOLS
    ]

    # Read accumulated conversation context
    known_parameters = state.get("parameters") or {}
    known_entities = state.get("entities") or {}

    # Get only the latest user message
    last_user_message = state["messages"][-1]

    if not isinstance(last_user_message, HumanMessage):
        raise ValueError("Latest message must be a user message")

    # Build the understanding prompt
    system_message = SystemMessage(
        content=UNDERSTANDING_PROMPT.format(
            parameters=parameters,
            tools=tools,
            known_parameters=known_parameters,
            known_entities=list(known_entities.values()),
        )
    )

    # Extract structured understanding using shared LLM client
    result = await llm_client.structured_completion(
        messages=[system_message, last_user_message],
        response_schema=UnderstandingResult,
    )

    if not isinstance(result, UnderstandingResult):
        raise ValueError("Invalid understanding result")

    # LangGraph reducer handles parameter accumulation
    return {
        "parameters": result.parameters,
        "requests": [
            request.model_dump() for request in result.requests
        ],
    }
