from uuid import uuid4

from langgraph.config import get_stream_writer

from app.agent.schemas.execution import MappedEntity, ParameterValue
from app.agent.schemas.resolution import (
    ReadyRequest,
    ResolvedRequest,
    ResolvedRequestData,
)
from app.agent.state import AgentState, AgentStateUpdate
from app.agent.utils.entities import entity_label, merge_references
from app.agent.utils.references import check_references
from app.configurations.tools.registry import TOOLS_BY_CODE
from app.core.settings import settings


# validate and merge the follow up requests & add request id
def request_resolver_node(state: AgentState) -> AgentStateUpdate:
    writer = get_stream_writer()
    writer({"node": "request_resolver", "status": "started", "data": {}})

    # Previous requests, by id (read only: collect saves the history)
    previous_by_id: dict[str, ReadyRequest] = {
        item["id"]: item for item in state.get("recent_requests", [])
    }

    entities = state.get("entities", {})
    message = str(state["messages"][-1].content)
    label_by_reference = {
        card["reference"]: entity_label(entities[card["reference"]])
        for card_list in state.get("visible_entities", [])
        for card in card_list["items"]
        if card["reference"] in entities
    }

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

        # The results the user pointed at must be backed by their own words
        question = check_references(request, label_by_reference, message)
        if question:
            resolved_requests.append(
                {"id": request_id, "status": "needs_clarification", "error": question}
            )
            continue

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
            if param["operation"] == "set":
                parameters[param["code"]] = param["value"]

            elif param["operation"] == "remove":
                parameters.pop(param["code"], None)

        # The referenced entity's own values (e.g. its id) are facts: they replace any guess
        parameters.update(
            fill_tool_parameter_from_entity(
                request["tool"], request["referenced_entities"], entities
            )
        )

        # Inherit previous entity references and add the new ones
        referenced_entities = merge_references(
            previous["request"].get("referenced_entities", []) if previous else [],
            request["referenced_entities"],
        )

        # Build resolved request
        resolved: ResolvedRequestData = {
            "question": request["question"],
            "tool": request["tool"],
            "referenced_entities": referenced_entities,
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

        # A later request in this same message may follow up on this one
        previous_by_id[request_id] = ready_request

    writer(
        {
            "node": "request_resolver",
            "status": "completed",
            "data": {"requests": resolved_requests},
        }
    )

    return {"resolved_requests": resolved_requests}


def fill_tool_parameter_from_entity(
    tool_code: str, references: list[str], entities: dict[str, MappedEntity]
) -> dict[str, ParameterValue]:
    """The tool's parameters the referenced entity has as attributes (e.g. product_id).

    Only for one entity: Understanding makes one request per entity when a tool takes one.
    """
    tool = TOOLS_BY_CODE.get(tool_code)
    if tool is None or len(references) != 1 or references[0] not in entities:
        return {}
    attributes = entities[references[0]]["attributes"]
    return {
        code: attributes[code]
        for code in [*tool.required_parameters, *tool.optional_parameters]
        if isinstance(attributes.get(code), str | int | float | bool)
    }
