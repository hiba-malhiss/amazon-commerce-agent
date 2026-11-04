from app.agent.schemas.resolution import RequestOutcome
from app.agent.state import AgentState, AgentStateUpdate


def collect_node(state: AgentState) -> AgentStateUpdate:
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

    return {"collected_outcomes": collected}
