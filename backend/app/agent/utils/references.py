"""
Validate the product references identified by the AI against the results visible to the user.

- Ensure every referenced product is visible.
- Verify that the reference is grounded in the user's message or the referenced product's name.
- Detect ambiguity when a description matches multiple products.
- Ask the user for clarification when a reference is invalid or ambiguous.
"""

import re
import unicodedata

from app.agent.schemas.resolution import UnderstoodRequestData


def check_references(
    request: UnderstoodRequestData, label_by_reference: dict[str, str], message: str
) -> str | None:
    references = request["referenced_entities"]
    if not references:
        return None

    # Only results the user can see (with none visible, the schema can't enforce this)
    if any(reference not in label_by_reference for reference in references):
        return "Which item do you mean?" if label_by_reference else "There are no results yet."

    quote = request["reference_quote"] or ""

    in_message = quote_in_message(quote, message)
    if not in_message and not quote_names_references(quote, references, label_by_reference):
        return "Which item do you mean?"

    if in_message:
        named, says_more = named_cards(quote, label_by_reference)
        if len(references) == 1 and references[0] in named and len(named) > 1 and not says_more:
            return f"Which one do you mean: {' or '.join(label_by_reference[r] for r in named)}?"
    return None


def quote_names_references(
    quote: str, references: list[str], label_by_reference: dict[str, str]
) -> bool:
    """True when the quote is largely the referenced results' label: at least half of its
    words appear in their labels. Lets the model quote the result it resolved a pronoun to
    ("INSIGNIA 43"), but not an invented position ("the first option").

    Language-agnostic on purpose: it compares the quote's words to the label's words, so it
    works whatever language the user (and the labels) are in — no hard-coded filler words,
    which would only ever cover one language. A few connectives ("the") stay in the quote,
    but the half-or-more rule tolerates them."""
    quote_words = words(quote)
    if not quote_words:
        return False
    label_words = set().union(*(words(label_by_reference[reference]) for reference in references))
    in_label = quote_words & label_words
    return len(in_label) * 2 >= len(quote_words)


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
    """Every word of the quote is in the message ("the first one" fits "the first and the
    fifth one"): the model can rephrase the user's words, not add its own."""
    quote_words = words(quote)
    return bool(quote_words) and quote_words <= words(message)


def words(text: str) -> set[str]:
    return set(re.findall(r"\w+", fold(text)))


def fold(text: str) -> str:
    """Text as it's compared: compatibility forms unified, case folded, spaces collapsed."""
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())
