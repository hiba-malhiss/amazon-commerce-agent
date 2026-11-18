"""Regression tests for deterministic card selection.

Card selection and ordering live in application code (not the response LLM):
- `numbered_cards` picks and numbers the cards, capped by `max_cards_per_reply`.
- `collect_node` records those exact cards (in order) as the list the user can point at.
- `visible_briefs` is what the Understanding step reads for positional references
  ("the first option" = number 1 of the most recent list).

These guard card count, order, and the data positional references resolve against.
"""

import pytest

from app.agent.nodes import collect as collect_module
from app.agent.nodes.collect import collect_node
from app.agent.utils.entities import numbered_cards, visible_briefs
from app.core import settings as settings_module


@pytest.fixture
def no_stream(monkeypatch):
    """collect_node emits trace events via the graph stream writer; stub it for unit tests."""
    monkeypatch.setattr(collect_module, "get_stream_writer", lambda: lambda _event: None)


def entity(ref: str, position: int, name: str = "") -> dict:
    return {
        "reference": ref,
        "position": position,
        "entity_code": "product",
        "attributes": {"product_name": name or ref, "price": position},
    }


def success(request_id: str, refs: list[str]) -> dict:
    return {
        "id": request_id,
        "status": "success",
        "result": {"type": "entities", "entities": [entity(r, i + 1) for i, r in enumerate(refs)]},
        "missing_parameters": [],
        "error": None,
    }


# ---- count --------------------------------------------------------------
# ISSUE/DECISION: how many cards the user sees must be governed by configuration
# (max_cards_per_reply), not chosen by the response LLM.
def test_card_count_capped_by_config(monkeypatch):
    monkeypatch.setattr(settings_module.settings, "max_cards_per_reply", 3)
    outcome = success("r1", [f"product_{i}" for i in range(10)])

    cards = numbered_cards([outcome], [])

    assert len(cards) == 3  # config caps it, not the reply
    assert [c["number"] for c in cards] == [1, 2, 3]


# ---- order --------------------------------------------------------------
# ISSUE: cards and the reply text disagreed on order (an off-topic result was card #1 but
# dropped from the prose), so "the first option" was ambiguous. Cards are ordered
# deterministically by result order here; the reply is told to follow that same order.
def test_card_order_follows_result_order():
    outcome = success("r1", ["product_a", "product_b", "product_c"])

    cards = numbered_cards([outcome], [])

    assert [c["entity"]["reference"] for c in cards] == ["product_a", "product_b", "product_c"]
    assert [c["number"] for c in cards] == [1, 2, 3]


def test_each_entity_numbered_once_across_outcomes():
    outcomes = [
        success("r1", ["product_a", "product_b"]),
        success("r2", ["product_b", "product_c"]),
    ]

    cards = numbered_cards(outcomes, [])

    # product_b appears in both results but is one card, keeping its first position
    assert [c["entity"]["reference"] for c in cards] == ["product_a", "product_b", "product_c"]
    assert [c["number"] for c in cards] == [1, 2, 3]


# ---- the visible list matches the shown cards ---------------------------
# ISSUE: the list used for later reference resolution must be exactly the cards shown, in the
# same order — otherwise "the Nth option" points at something the user never saw as Nth.
def ready(request_id: str) -> dict:
    return {"id": request_id, "status": "ready", "request": {"referenced_entities": []}}


def test_collect_records_visible_list_matching_the_cards(no_stream):
    outcome = success("r1", ["product_a", "product_b", "product_c"])
    state = {
        "resolved_requests": [ready("r1")],
        "outcomes": [outcome],
        "visible_entities": [],
        "entities": {},
    }

    update = collect_node(state)

    cards = numbered_cards(update["collected_outcomes"], [])
    visible = update["visible_entities"]
    assert len(visible) == 1
    # The recorded list is exactly the shown cards, in the same order
    assert [item["reference"] for item in visible[0]["items"]] == [
        c["entity"]["reference"] for c in cards
    ]


def test_collect_adds_no_list_for_a_single_result(no_stream):
    outcome = success("r1", ["product_a"])
    state = {
        "resolved_requests": [ready("r1")],
        "outcomes": [outcome],
        "visible_entities": [],
        "entities": {},
    }

    update = collect_node(state)

    assert update["visible_entities"] == []  # a single card is not a new list to point at


# ---- positional reference data -----------------------------------------
# ISSUE: "the first option" resolved to an older results list instead of the last one the
# user saw. Understanding reads positional references from visible_briefs, so the most recent
# list must come first and be numbered from 1 — then "the first option" = briefs[0][0].
def test_visible_briefs_newest_first_numbered_from_one():
    entities = {
        "product_a": entity("product_a", 1, "A"),
        "product_b": entity("product_b", 2, "B"),
        "product_c": entity("product_c", 1, "C"),
    }
    older = {"items": [{"reference": "product_a", "request_id": "r1"}]}
    newer = {
        "items": [
            {"reference": "product_c", "request_id": "r2"},
            {"reference": "product_b", "request_id": "r2"},
        ]
    }
    visible_entities = [older, newer]  # stored oldest -> newest

    briefs = visible_briefs(visible_entities, entities)

    # Newest list first, so "the first option" = briefs[0][0]
    assert briefs[0][0]["reference"] == "product_c"
    assert [card["number"] for card in briefs[0]] == [1, 2]
    assert briefs[1][0]["reference"] == "product_a"
