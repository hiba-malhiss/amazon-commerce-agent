from collections.abc import Iterable

from pydantic import JsonValue

from app.agent.schemas.execution import MappedEntity
from app.agent.schemas.resolution import (
    NumberedCard,
    ReadyRequest,
    RequestOutcome,
    VisibleEntityList,
)
from app.configurations.entities.registry import ENTITIES_BY_CODE
from app.core.settings import settings

# Long text (e.g. a product's title) is cut to this in a brief
MAX_BRIEF_TEXT = 80


def merge_references(previous: list[str], new: list[str]) -> list[str]:
    """Previous references first, then the new ones; each reference once, order kept."""
    # dict.fromkeys works as a set that keeps the order
    return list(dict.fromkeys([*previous, *new]))


def entities_in_use(
    requests: Iterable[ReadyRequest],
    visible_entities: Iterable[VisibleEntityList],
    stored: dict[str, MappedEntity],
) -> dict[str, MappedEntity]:
    """The stored entities still needed: what requests referred to and what the kept
    card lists show. Order kept, each once."""
    referenced = [
        reference
        for request in requests
        for reference in request["request"].get("referenced_entities", [])
    ]
    shown = [card["reference"] for card_list in visible_entities for card in card_list["items"]]
    return {
        reference: stored[reference]
        for reference in dict.fromkeys([*referenced, *shown])
        if reference in stored
    }


def entity_label(entity: MappedEntity) -> str:
    """How the user knows the entity: its config's label attribute, else its reference."""
    config = ENTITIES_BY_CODE.get(entity["entity_code"])
    value = (
        entity["attributes"].get(config.label_parameter)
        if config and config.label_parameter
        else None
    )
    return str(value).strip() if value not in (None, "") else entity["reference"]


def numbered_cards(
    outcomes: Iterable[RequestOutcome], visible_entities: Iterable[VisibleEntityList]
) -> list[NumberedCard]:
    """This turn's results as the user sees them: one numbered row of cards.

    Successful requests in order, each one's results in the API's order, each entity once,
    up to max_cards_per_reply. When every card is already on screen (e.g. one product's
    details, a comparison), each keeps the number it has there, so "the fifth one" keeps
    meaning the same product. collect saves them, respond answers by them, and the
    service stores them for the UI.
    """
    cards: dict[str, NumberedCard] = {}  # by reference, so each entity gets one card
    for outcome in outcomes:
        if outcome["status"] != "success" or not outcome["result"]:
            continue
        for entity in outcome["result"]["entities"]:
            if len(cards) == settings.max_cards_per_reply:
                break
            cards.setdefault(
                entity["reference"],
                {"number": len(cards) + 1, "request_id": outcome["id"], "entity": entity},
            )

    # Each visible product's number in the newest list that shows it
    visible_number = {
        card["reference"]: number
        for card_list in visible_entities
        for number, card in enumerate(card_list["items"], start=1)
    }
    if cards and all(reference in visible_number for reference in cards):
        return [{**card, "number": visible_number[ref]} for ref, card in cards.items()]
    return list(cards.values())


def visible_briefs(
    visible_entities: Iterable[VisibleEntityList], entities: dict[str, MappedEntity]
) -> list[list[dict[str, JsonValue]]]:
    """The cards the user can still point at, as Understanding sees them: one list per
    reply (newest first), each card with its reference, number, request and the entity's
    brief_parameters."""
    return [
        [
            {
                "reference": card["reference"],
                "number": number,
                "request_id": card["request_id"],
                **entity_brief(entities[card["reference"]]),
            }
            for number, card in enumerate(card_list["items"], start=1)
            if card["reference"] in entities
        ]
        for card_list in reversed(list(visible_entities))
    ]


def entity_brief(entity: MappedEntity) -> dict[str, JsonValue]:
    """The entity's brief_parameters (from its config), long text cut short."""
    config = ENTITIES_BY_CODE.get(entity["entity_code"])
    brief = (
        {code: entity["attributes"].get(code) for code in config.brief_parameters} if config else {}
    )
    return {
        code: value[:MAX_BRIEF_TEXT] if isinstance(value, str) else value
        for code, value in brief.items()
        if value is not None
    }
