from uuid import uuid4

from langgraph.config import get_stream_writer

from app.agent.schemas.execution import ParameterValue
from app.agent.schemas.resolution import (
    ReadyRequest,
    ResolvedRequest,
    ResolvedRequestData,
)
from app.agent.state import AgentState, AgentStateUpdate
from app.core.settings import settings


def request_resolver_node(state: AgentState) -> AgentStateUpdate:
    writer = get_stream_writer()
    writer({"node": "request_resolver", "status": "started", "data": {}})

    # Load previous resolved requests
    history: list[ReadyRequest] = list(state.get("recent_requests", []))

    previous_by_id: dict[str, ReadyRequest] = {item["id"]: item for item in history}

    resolved_requests: list[ResolvedRequest] = []
    requests = state.get("requests", [])

    # Check request limit
    if len(requests) > settings.max_requests_per_turn:
        writer(
            {
                "node": "request_resolver",
                "status": "failed",
                "data": {"error": "Too many requests", "requests": len(requests)},
            }
        )
        return {
            "resolved_requests": [
                {
                    "id": uuid4().hex,
                    "status": "needs_clarification",
                    "error": "Too many requests. Ask the user to prioritize.",
                }
            ]
        }

    for request in requests:
        request_id = uuid4().hex
        source_id = request["source_request_id"]

        # Find the referenced previous request
        previous = previous_by_id.get(source_id) if source_id else None

        if (
            request["relation"] == "ambiguous"
            or (source_id and previous is None)
            or (request["relation"] == "follow_up" and previous is None)
        ):
            resolved_requests.append(
                {
                    "id": request_id,
                    "status": "needs_clarification",
                    "error": "Which previous request do you mean?",
                }
            )
            continue

        # Inherit previous parameters
        parameters: dict[str, ParameterValue] = (
            dict(previous["request"]["parameters"]) if previous else {}
        )

        # Apply parameter changes
        for param in request["parameters"]:
            if param["operation"] == "set" and param["value"] is not None:
                parameters[param["code"]] = param["value"]

            elif param["operation"] == "remove":
                parameters.pop(param["code"], None)

        # Build resolved request
        resolved: ResolvedRequestData = {
            "question": request["question"],
            "tool": request["tool"],
            "entities": request["entities"],
            "parameters": parameters,
            "relation": request["relation"],
            "source_request_id": source_id,
        }

        ready_request: ReadyRequest = {
            "id": request_id,
            "status": "ready",
            "request": resolved,
        }

        resolved_requests.append(ready_request)

        # Save same request for future follow-ups
        history.append(ready_request)
        previous_by_id[request_id] = ready_request

    writer(
        {
            "node": "request_resolver",
            "status": "completed",
            "data": {"requests": resolved_requests},
        }
    )

    return {
        "resolved_requests": resolved_requests,
        "recent_requests": history[-settings.max_recent_requests :],
    }
