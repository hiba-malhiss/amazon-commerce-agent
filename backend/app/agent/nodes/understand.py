from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langgraph.config import get_stream_writer
from langgraph.types import Overwrite

from app.agent.prompts.understanding import UNDERSTANDING_PROMPT
from app.agent.schemas.understanding import UnderstandingResult, understanding_schema
from app.agent.state import AgentState, AgentStateUpdate
from app.agent.utils.entities import visible_briefs
from app.agent.utils.prompts import emit_prompt
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

    tools = [
        {
            "code": t.code,
            "name": t.name,
            "description": t.description,
            "required_parameters": t.required_parameters,
            "optional_parameters": t.optional_parameters,
        }
        for t in TOOLS
    ]

    # Get only the latest user message
    last_user_message = state["messages"][-1]

    if not isinstance(last_user_message, HumanMessage):
        return understanding_failed("Invalid user message")

    # Recent requests (newest first)
    recent_requests = [
        {
            "id": item["id"],
            "question": item["request"]["question"],
            "tool": item["request"]["tool"],
            "parameters": item["request"]["parameters"],
        }
        for item in state.get("recent_requests", [])[::-1]
    ]

    # The results the user can point at: a brief of each, never the full entity
    visible_results = visible_briefs(state.get("visible_entities", []), state.get("entities", {}))
    references = [card["reference"] for card_list in visible_results for card in card_list]

    # Build Understanding context
    system_message = SystemMessage(
        content=UNDERSTANDING_PROMPT.format(
            parameters=parameters,
            tools=tools,
            recent_requests=recent_requests,
            visible_results=visible_results,
        )
    )

    history = trim_messages(
        state["messages"][-settings.max_history_messages :],
        max_tokens=settings.max_history_tokens,
        token_counter="approximate",
        strategy="last",
        start_on="human",
    )
    messages = [system_message, *history]

    # Check the input token budget
    if count_tokens_approximately(messages) > settings.max_understanding_input_tokens:
        return understanding_failed("Understanding input exceeds token budget")

    emit_prompt("understand", messages)

    # Extract structured requests
    try:
        result = await llm_client.structured_completion(
            messages=messages,
            response_schema=understanding_schema(references),
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
