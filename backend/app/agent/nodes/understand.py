from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.types import Overwrite

from app.agent.prompts.understanding import UNDERSTANDING_PROMPT
from app.agent.schemas.understanding import UnderstandingResult
from app.agent.state import AgentState, AgentStateUpdate
from app.configurations.parameters import PARAMETERS
from app.configurations.tools.registry import TOOLS
from app.core.settings import settings
from app.llm.client import llm_client


def understanding_failed(reason: str) -> AgentStateUpdate:
    return {
        "requests": [],
        "resolved_requests": [],
        "outcomes": Overwrite([]),
        "collected_outcomes": [
            {
                "id": "understand",
                "status": "fail",
                "result": None,
                "missing_parameters": [],
                "error": reason,
            }
        ],
        "reply": None,
    }


async def understand_node(state: AgentState) -> AgentStateUpdate:
    # Load configurations
    parameters = [p.model_dump() for p in PARAMETERS]
    tools = [{"code": t.code, "name": t.name, "description": t.description} for t in TOOLS]

    # Load recent requests (newest first) and known entities
    recent_requests = state.get("recent_requests", [])[-settings.max_recent_requests :][::-1]
    known_entities = state.get("entities", {})

    # Get only the latest user message
    last_user_message = state["messages"][-1]

    if not isinstance(last_user_message, HumanMessage):
        return understanding_failed("Invalid user message")

    # Build Understanding context
    system_message = SystemMessage(
        content=UNDERSTANDING_PROMPT.format(
            parameters=parameters,
            tools=tools,
            recent_requests=recent_requests,
            known_entities=list(known_entities.values()),
        )
    )

    messages = [system_message, last_user_message]

    # Check the input token budget
    if count_tokens_approximately(messages) > settings.max_understanding_input_tokens:
        return understanding_failed("Understanding input exceeds token budget")

    # Extract structured requests
    try:
        result = await llm_client.structured_completion(
            messages=messages,
            response_schema=UnderstandingResult,
        )
    except Exception:
        return understanding_failed("Unable to process the request")

    if not isinstance(result, UnderstandingResult):
        return understanding_failed("Invalid understanding result")

    # Start a new turn: reset everything that belongs to the current message
    return {
        "requests": [request.model_dump() for request in result.requests],
        "resolved_requests": [],
        "outcomes": Overwrite([]),
        "collected_outcomes": [],
        "reply": None,
    }
