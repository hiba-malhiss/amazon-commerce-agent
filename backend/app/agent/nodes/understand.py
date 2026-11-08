from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.config import get_stream_writer
from langgraph.types import Overwrite

from app.agent.prompts.understanding import UNDERSTANDING_PROMPT
from app.agent.schemas.understanding import UnderstandingResult
from app.agent.state import AgentState, AgentStateUpdate
from app.configurations.parameters import PARAMETERS
from app.configurations.tools.registry import TOOLS
from app.core.settings import settings
from app.llm.client import llm_client


def understanding_failed(reason: str) -> AgentStateUpdate:
    get_stream_writer()({"node": "understand", "status": "failed", "data": {"error": reason}})
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
        "out_of_scope": False,
        "out_of_scope_reason": None,
    }


async def understand_node(state: AgentState) -> AgentStateUpdate:
    writer = get_stream_writer()
    writer(
        {
            "node": "understand",
            "status": "started",
            "data": {"recent_requests": state.get("recent_requests", [])},
        }
    )

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

    writer(
        {
            "node": "understand",
            "status": "completed",
            "data": {
                # Pydantic models → plain dicts, so the event can be sent as JSON
                "requests": [request.model_dump(mode="json") for request in result.requests],
                "out_of_scope": result.out_of_scope,
                "out_of_scope_reason": result.out_of_scope_reason,
            },
        }
    )

    # Start a new turn: reset everything that belongs to the current message
    return {
        "requests": [request.model_dump() for request in result.requests],
        "resolved_requests": [],
        "outcomes": Overwrite([]),
        "collected_outcomes": [],
        "out_of_scope": result.out_of_scope,
        "out_of_scope_reason": result.out_of_scope_reason if result.out_of_scope else None,
    }
