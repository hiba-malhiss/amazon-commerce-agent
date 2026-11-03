from typing import Any
from uuid import uuid4

from app.agent.schemas.resolution import (
    RequestHistoryEntry,
    ResolvedRequest,
)
from app.agent.schemas.understanding import Request
from app.agent.state import AgentState


# merge parameters for the follow up request and validate requests
def request_resolver_node(state: AgentState) -> dict[str, Any]:
    # Load previous requests
    history: list[RequestHistoryEntry] = list(state.get("recent_requests", []))

    previous_by_id: dict[str, RequestHistoryEntry] = {item["id"]: item for item in history}
    resolved_requests: list[ResolvedRequest] = []

    for raw_request in state.get("requests", []):
        request = Request.model_validate(raw_request)
        request_id = uuid4().hex

        # Find the referenced request
        previous = previous_by_id.get(request.source_request_id)

        if (
            request.relation == "ambiguous"
            or (request.source_request_id and previous is None)
            or (request.relation == "follow_up" and previous is None)
        ):
            resolved_requests.append(
                {
                    "id": request_id,
                    "status": "needs_clarification",
                    "error": "Which previous request do you mean?",
                }
            )
            continue

        # Start with referenced parameters, if any
        parameters = previous["parameters"].copy() if previous else {}

        for param in request.parameters:
            if param.operation == "set" and param.value is not None:
                parameters[param.code] = param.value

            elif param.operation == "remove":
                parameters.pop(param.code, None)

        # Prepare the resolved request
        resolved = {
            **request.model_dump(),
            "parameters": parameters,
        }

        resolved_requests.append(
            {
                "id": request_id,
                "status": "ready",
                "request": resolved,
            }
        )

        # Save for future follow-ups
        summary = {
            "id": request_id,
            "question": request.question,
            "tool": request.tool,
            "parameters": parameters,
            "entities": request.entities,
            "status": "ready",
        }

        history.append(summary)
        previous_by_id[request_id] = summary

    return {
        "resolved_requests": resolved_requests,
        "recent_requests": history[-8:],
    }
