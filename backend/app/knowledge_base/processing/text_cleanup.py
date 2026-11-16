"""Text cleanup helpers for extracted document content."""

import re
import unicodedata

# Match a word ending with an actual line-wrap hyphen.
# Supports common Unicode hyphen characters.
_WRAP_HYPHEN = re.compile(r"(\w)[-‐‑\u00ad]+$")


# "ﬁle" => "file"
def normalize_unicode(text: str) -> str:
    """Normalize ligatures and compatibility characters."""
    return unicodedata.normalize("NFKC", text)


# incase a word with - get split into 2 lines
def join_hyphenated(previous: str, nxt: str) -> str | None:
    """Join a hyphenated word continued on the next line."""

    # The next line must begin with a lowercase letter.
    if not nxt[:1].islower():
        return None

    # The previous line must end with a hyphenated word.
    if not _WRAP_HYPHEN.search(previous):
        return None

    # Remove the wrap hyphen and join the two parts.
    return _WRAP_HYPHEN.sub(r"\1", previous) + nxt
