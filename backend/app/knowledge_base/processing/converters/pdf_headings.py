"""Detect PDF headings using font sizes, bold text, and section numbers.

PDF files don't have Markdown headings (#, ##, ###).
We estimate heading levels using text formatting.

Rules:
1. Find the most common font size (body text).
2. Larger font sizes become headings.
3. Numbered sections can be headings even at body size.
4. Slightly larger bold text can also be a heading.
5. Very small text is treated as page chrome.
"""

import re
from collections import Counter
from dataclasses import dataclass

# Font must be at least 15% larger than body text
# to be classified as a heading based on size alone.
HEADING_FACTOR = 1.15

# Text smaller than 75% of body font size is ignored.
CHROME_FLOOR = 0.75

# Long lines are usually paragraphs, not headings.
HEADING_MAX_CHARS = 100

# Lines ending with these characters are likely sentences.
SENTENCE_END = (".", ",", ";")

# Examples:
# "I. Introduction"
# "A. Scope"
# "1. Background"
#
# The section title must contain letters and allowed
# punctuation, but no digits inside the title.
NUMBERED_SECTION = re.compile(r"^(?:[IVX]{1,5}|[A-Z]|[1-9]\d?)\.\s+[A-Z][A-Za-z '\-]{2,}$")


@dataclass(frozen=True)
class HeadingModel:
    """Font information used to classify headings."""

    body_size: float

    # Maps font sizes to Markdown heading levels.
    # Example: {20.0: 1, 16.0: 2}
    levels: dict[float, int]

    # Level assigned to numbered or slightly larger bold headings.
    numbered_level: int


def build_model(sizes: list[float]) -> HeadingModel:
    """Determine body font size and heading levels."""

    # Step 1: Find the most common font size.
    # We assume the most frequently used size is body text.
    if sizes:
        body_size = Counter(sizes).most_common(1)[0][0]
    else:
        body_size = 0.0

    # Step 2: Find font sizes that are at least 15% larger
    # than the body font size.
    heading_sizes = set()

    for size in sizes:
        if size >= body_size * HEADING_FACTOR:
            heading_sizes.add(size)

    # Step 3: Sort from largest to smallest.
    # Largest font becomes H1, next becomes H2, etc.
    sorted_sizes = sorted(heading_sizes, reverse=True)

    # Step 4: Map each heading font size to a Markdown level.
    levels = {}

    for level, size in enumerate(sorted_sizes, start=1):
        levels[size] = level

    # Numbered headings are placed one level deeper
    # than the smallest font-based heading.
    numbered_level = len(levels) + 1

    return HeadingModel(
        body_size=body_size,
        levels=levels,
        numbered_level=numbered_level,
    )


def is_chrome(text: str, size: float, model: HeadingModel) -> bool:
    """Check whether a line is too small to be normal body text.

    Small text is treated as page chrome, such as
    headers, footers, or page markers.
    """

    if not text:
        return False

    minimum_size = model.body_size * CHROME_FLOOR

    return size < minimum_size


def heading_level(
    text: str,
    size: float,
    bold: bool,
    model: HeadingModel,
) -> int | None:
    """Return a Markdown heading level, or None for body text."""

    # Rule 1: Numbered sections are always headings.
    # Example: "1. Introduction" or "A. Scope"
    if NUMBERED_SECTION.match(text):
        return model.numbered_level

    # Rule 2: Long lines are not headings.
    if len(text) > HEADING_MAX_CHARS:
        return None

    # Rule 3: Lines ending with .,; are treated as sentences.
    if text.endswith(SENTENCE_END):
        return None

    # Rule 4: Large font sizes become headings.
    if size in model.levels:
        return model.levels[size]

    # Rule 5: Bold lines slightly larger than body text
    # are also considered headings.
    if bold and size > model.body_size:
        return model.numbered_level

    # Otherwise, ordinary body text.
    return None
