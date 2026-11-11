"""Checks on the visible results Understanding says the user pointed at."""

import re
import unicodedata

from app.agent.schemas.resolution import UnderstoodRequestData


def check_references(
    request: UnderstoodRequestData, label_by_reference: dict[str, str], message: str
) -> str | None:
    """A question to ask when the results the user pointed at can't be trusted, else None.

    - the quote must be in the user's message (the model can't invent a reference)
    - code also reads the names in the quote: "the JBL one" with two JBL cards is asked
      about even when the model picked one
    """
    references = request["referenced_entities"]
    if not references:
        return None

    quote = request["reference_quote"] or ""
    if not quote_in_message(quote, message):
        return "Which item do you mean?"

    named, says_more = named_cards(quote, label_by_reference)
    if len(references) == 1 and references[0] in named and len(named) > 1 and not says_more:
        return f"Which one do you mean: {' or '.join(label_by_reference[r] for r in named)}?"
    return None


def named_cards(quote: str, label_by_reference: dict[str, str]) -> tuple[list[str], bool]:
    """Code's own reading of the quote, by names only: the cards whose label has every name
    in the quote ("jbl", "white", "s24"), and whether the quote says more than names ("the
    cheaper JBL"), which only the model can judge."""
    words_by_reference = {ref: words(label) for ref, label in label_by_reference.items()}
    label_words = set().union(*words_by_reference.values())
    quote_words = words(quote)
    names = {word for word in quote_words & label_words if not word.isdigit()}
    says_more = any(len(word) > 3 for word in quote_words - label_words)
    named = [ref for ref, label in words_by_reference.items() if names and names <= label]
    return named, says_more


def quote_in_message(quote: str, message: str) -> bool:
    return len(fold(quote)) >= 2 and fold(quote) in fold(message)


def words(text: str) -> set[str]:
    return set(re.findall(r"\w+", fold(text)))


def fold(text: str) -> str:
    """Text as it's compared: compatibility forms unified, case folded, spaces collapsed."""
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())
