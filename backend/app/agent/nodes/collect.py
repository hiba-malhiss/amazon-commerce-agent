from langgraph.config import get_stream_writer

from app.agent.schemas.resolution import ReadyRequest, RequestOutcome
from app.agent.state import AgentState, AgentStateUpdate
from app.agent.utils.entities import entities_in_use, extract_found_entities
from app.core.settings import settings


# final state after workflows
def collect_node(state: AgentState) -> AgentStateUpdate:
    writer = get_stream_writer()
    writer({"node": "collect", "status": "started", "data": {}})

    outcomes_by_id = {outcome["id"]: outcome for outcome in state.get("outcomes", [])}
    collected: list[RequestOutcome] = []

    # Preserve the original request order
    for request in state["resolved_requests"]:
        if request["status"] == "needs_clarification":
            collected.append(
                {
                    "id": request["id"],
                    "status": "needs_clarification",
                    "result": None,
                    "missing_parameters": [],
                    "error": request["error"],
                }
            )
            continue

        outcome = outcomes_by_id.get(request["id"])

        if outcome is None:
            outcome: RequestOutcome = {
                "id": request["id"],
                "status": "fail",
                "result": None,
                "missing_parameters": [],
                "error": "Request completed without an outcome",
            }

        collected.append(outcome)

    # collect entities: save them at the state level and the references on the request,
    # to avoid duplication
    found, references_by_request = extract_found_entities(collected)

    # Add this message's requests to the history, complete with their results.
    new_requests: list[ReadyRequest] = [
        {**request, "result_references": references_by_request[request["id"]]}
        if request["id"] in references_by_request
        else request
        for request in state["resolved_requests"]
        if request["status"] == "ready"
    ]
    recent_requests = [*state.get("recent_requests", []), *new_requests][
        -settings.max_recent_requests :
    ]

    entities = entities_in_use(recent_requests, {**state.get("entities", {}), **found})

    writer(
        {
            "node": "collect",
            "status": "completed",
            "data": {"outcomes": collected, "entities": entities},
        }
    )
    return {
        "collected_outcomes": collected,
        "entities": entities,
        "recent_requests": recent_requests,
    }
