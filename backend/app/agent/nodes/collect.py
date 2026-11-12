from langgraph.config import get_stream_writer

from app.agent.schemas.resolution import ReadyRequest, RequestOutcome, VisibleEntityList
from app.agent.state import AgentState, AgentStateUpdate
from app.agent.utils.entities import entities_in_use, numbered_cards
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

    # Add this message's requests to the history
    new_requests: list[ReadyRequest] = [
        request for request in state["resolved_requests"] if request["status"] == "ready"
    ]
    recent_requests = [*state.get("recent_requests", []), *new_requests][
        -settings.max_recent_requests :
    ]

    # This turn's cards join the lists the user can point at, unless they're all already on
    # screen (details, a comparison) or a single result: those aren't a new list to pick from
    visible_entities = state.get("visible_entities", [])
    visible = {card["reference"] for card_list in visible_entities for card in card_list["items"]}
    cards = numbered_cards(collected, visible_entities)
    if len(cards) >= 2 and any(card["entity"]["reference"] not in visible for card in cards):
        card_list: VisibleEntityList = {
            "items": [
                {"reference": card["entity"]["reference"], "request_id": card["request_id"]}
                for card in cards
            ]
        }
        visible_entities = [*visible_entities, card_list][-settings.max_visible_entity_lists :]

    # Add this turn's card entities (fresh data replaces stored), then drop what's unused
    found = {card["entity"]["reference"]: card["entity"] for card in cards}
    entities = entities_in_use(
        recent_requests, visible_entities, {**state.get("entities", {}), **found}
    )

    writer(
        {
            "node": "collect",
            "status": "completed",
            "data": {
                "outcomes": collected,
                "entities": entities,
                "visible_entities": visible_entities,
            },
        }
    )
    return {
        "collected_outcomes": collected,
        "entities": entities,
        "recent_requests": recent_requests,
        "visible_entities": visible_entities,
    }
