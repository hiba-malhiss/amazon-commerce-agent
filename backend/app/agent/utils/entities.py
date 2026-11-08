from collections.abc import Iterable

from app.agent.schemas.execution import MappedEntity
from app.agent.schemas.resolution import ReadyRequest, RequestOutcome


def merge_references(previous: list[str], new: list[str]) -> list[str]:
    """Previous references first, then the new ones; each reference once, order kept."""
    # dict.fromkeys works as a set that keeps the order
    return list(dict.fromkeys([*previous, *new]))


def extract_found_entities(
    outcomes: Iterable[RequestOutcome],
    limit: int,
) -> tuple[dict[str, MappedEntity], dict[str, list[str]]]:
    """What successful requests found (top `limit` each).

    Returns the entities by reference, and each request's references in result order.
    """
    found: dict[str, MappedEntity] = {}
    references_by_request: dict[str, list[str]] = {}

    for outcome in outcomes:
        if outcome["status"] != "success" or not outcome["result"]:
            continue
        top = outcome["result"]["entities"][:limit]
        for entity in top:
            found[entity["reference"]] = entity
        references_by_request[outcome["id"]] = [entity["reference"] for entity in top]

    return found, references_by_request


def entities_in_use(
    requests: Iterable[ReadyRequest],
    stored: dict[str, MappedEntity],
) -> dict[str, MappedEntity]:
    """Stored entities the requests point at: what the user referred to and what each found.

    Keeps the requests' order and each reference once; unknown references are skipped.
    """
    references = dict.fromkeys(
        reference
        for request in requests
        for reference in [
            *request["request"].get("referenced_entities", []),
            *request.get("result_references", []),
        ]
    )
    return {reference: stored[reference] for reference in references if reference in stored}
