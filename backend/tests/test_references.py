"""Regression tests for reference-quote grounding (`check_references`).

Each test guards a specific bug we hit while resolving "compare it to the Nth option".
"""

from app.agent.utils.references import check_references

# Several products share the word "INSIGNIA"; only "43"/"24" tell them apart.
LABELS = {
    "product_a": 'INSIGNIA 43" Class F50 Series LED 4K UHD Smart Fire TV',
    "product_b": 'INSIGNIA 24" Class F20 Series LED HD Smart Fire TV',
    "product_c": "Philips 40-Inch Class QLED 1080p Smart Roku TV",
}


def req(quote: str, refs: list[str]) -> dict:
    return {"reference_quote": quote, "referenced_entities": refs}


# ISSUE: "compare it to the third option" compared only the third — the "it" request was
# rejected with "Which item do you mean?". The model had resolved "it" to the in-focus
# product but quoted that product's NAME, and the guard only accepted words from the latest
# message. A quote that names the referenced (visible) product is valid grounding.
def test_quote_naming_the_referenced_product_is_accepted():
    result = check_references(
        req("INSIGNIA 43", ["product_a"]), LABELS, "compare it to the third option"
    )
    assert result is None


# ISSUE (same bug, cleaner path): the user's pronoun itself must resolve — "it" is grounded
# because it appears in the message.
def test_pronoun_quote_present_in_message_is_accepted():
    result = check_references(req("it", ["product_a"]), LABELS, "compare it to the third option")
    assert result is None


# ISSUE: the model replaced the user's "it" with an invented position "the first option"
# (a word the user never typed). That is NOT grounded and must still be rejected.
def test_invented_position_the_user_never_said_is_rejected():
    result = check_references(
        req("the first option", ["product_a"]), LABELS, "compare it to the third option"
    )
    assert result == "Which item do you mean?"


# REGRESSION GUARD: scoping rule 3 to in-message quotes must not disable it. The user's own
# words that fit 2+ shown products ("the INSIGNIA") still ask which one they mean.
def test_ambiguous_user_words_still_ask_which_one():
    result = check_references(
        req("the INSIGNIA", ["product_a"]), LABELS, "tell me about the INSIGNIA"
    )
    assert result is not None and result.startswith("Which one")


# The fix that unblocked the compare: quoting the resolved product's own name does NOT
# trip the ambiguity check (the model already committed to one product), even though the
# name shares "INSIGNIA" with other shown products.
def test_name_quote_is_not_treated_as_ambiguous():
    result = check_references(
        req("INSIGNIA 43", ["product_a"]), LABELS, "compare it to the third one"
    )
    assert result is None


# A plain positional reference uses the user's own words and resolves to one card.
def test_positional_reference_in_message_is_accepted():
    result = check_references(
        req("the third option", ["product_b"]), LABELS, "compare it to the third option"
    )
    assert result is None


# A reference to something not on screen is rejected.
def test_reference_to_a_non_visible_product_is_rejected():
    result = check_references(req("it", ["product_missing"]), LABELS, "compare it")
    assert result == "Which item do you mean?"
