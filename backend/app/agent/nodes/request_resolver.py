from uuid import uuid4

from app.agent.schemas.resolution import (
    ParameterValue,
    UnderstoodRequestData,
    ResolvedRequest,
    UnderstoodRequestData,
)
from app.agent.state import AgentState, AgentStateUpdate
from app.core.settings import settings


# Merge parameters for follow-up requests and validate references
def request_resolver_node(state: AgentState) -> AgentStateUpdate:
    # Load previous requests
    history: list[UnderstoodRequestData] = list(state.get("recent_requests", []))

    previous_by_id: dict[str, UnderstoodRequestData] = {item["id"]: item for item in history}
    resolved_requests: list[ResolvedRequest] = []

    for request in state.get("requests", []):
        request_id = uuid4().hex
        source_id = request["source_request_id"]

        # Find the referenced request
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

        # Start with referenced parameters, if any
        parameters: dict[str, ParameterValue] = dict(previous["parameters"]) if previous else {}

        for param in request.parameters:
            if param.operation == "set" and param.value is not None:
                parameters[param.code] = param.value

            elif param.operation == "remove":
                parameters.pop(param.code, None)

        # Prepare the resolved request
        resolved: UnderstoodRequestData = {
            **request.model_dump(),
            "parameters": parameters,
            "source_request_id": source_id,
        }

        resolved_requests.append({"id": request_id, "status": "ready", "request": resolved})

        # Save for future follow-ups
        summary: UnderstoodRequestData = {
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
        "recent_requests": history[-settings.max_recent_requests :],
    }
