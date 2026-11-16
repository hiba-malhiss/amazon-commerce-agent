"""Split Markdown documents into sections using headings.

Steps:
1. Read the Markdown line by line.
2. Start a new section whenever we find a heading (#, ##, ###).
3. Keep the heading path and page numbers in metadata.
4. Optionally merge small neighboring sections.

This file does not generate embeddings.
"""

import re

from haystack import Document

from .tokens import count_tokens

# Matches Markdown headings such as #, ##
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

# Markdown code block markers.
# Headings inside code blocks should not create new sections.
FENCES = ("```", "~~~")


def split_by_structure(documents: list[Document]) -> list[Document]:
    """Split all documents into sections based on Markdown headings."""

    all_sections = []

    for document in documents:
        sections = _split_one(document)
        all_sections.extend(sections)  # extend for list

    return all_sections


def _split_one(document: Document) -> list[Document]:
    """Split one Markdown document into sections."""

    sections = []

    # remove line_pages, store page_start and page_end instead.
    metadata = {key: value for key, value in document.meta.items() if key != "line_pages"}

    line_pages = document.meta.get("line_pages")

    # Track headings such as:
    # Returns > Electronics > Warranty
    headings = []
    section_path = ""

    # Text and page numbers belonging to the current section.
    current_lines = []
    current_pages = []

    # Tracks whether we are inside a Markdown code block.
    code_fence = None

    for index, line in enumerate((document.content or "").splitlines()):
        # Step 1: Detect the beginning/end of a code block.
        marker = line.strip()[:3]

        if marker in FENCES:
            if code_fence == marker:
                code_fence = None
            elif code_fence is None:
                code_fence = marker

        # Step 2: Check whether the line is a Markdown heading.
        # Ignore headings inside code blocks.
        heading = None

        if code_fence is None:
            heading = HEADING.match(line)

        # Step 3: A heading means a new section starts.
        if heading:
            # Save the previous section before starting a new one.
            _save_section(
                sections,
                current_lines,
                current_pages,
                section_path,
                metadata,
            )

            # Extract the heading level and title.
            # Example: "## Electronics" -> level=2, title="Electronics"
            level = len(heading.group(1))
            title = heading.group(2)

            # Update the heading hierarchy.
            section_path = _path(headings, level, title)

            # Start collecting text for the new section.
            current_lines = []
            current_pages = []

            # Include the heading's page in the section range.
            if line_pages:
                current_pages.append(line_pages[index])

        else:
            # Step 4: Add ordinary text to the current section.
            current_lines.append(line)

            if line_pages:
                current_pages.append(line_pages[index])

    # Save the last section after the loop finishes.
    _save_section(
        sections,
        current_lines,
        current_pages,
        section_path,
        metadata,
    )

    return sections


def _save_section(
    sections: list[Document],
    lines: list[str],
    pages: list[int],
    section_path: str,
    metadata: dict,
) -> None:
    """Save the current section if it contains text."""

    content = "\n".join(lines).strip()

    if not content:
        return

    # Keep the section path in both content and metadata.
    if section_path:
        content = f"{section_path}\n\n{content}"

    section_metadata = {
        **metadata,
        "section_path": section_path or None,
        **_page_range(pages),
    }

    sections.append(
        Document(
            content=content,
            meta=section_metadata,
        )
    )


def _path(
    headings: list[tuple[int, str]],
    level: int,
    title: str,
) -> str:
    """Update the current heading hierarchy.

    Example:
        # Returns       -> Returns
        ## Electronics  -> Returns > Electronics
        ### Warranty    -> Returns > Electronics > Warranty
    """

    # Remove headings at the same or deeper level.
    # Example: a new H2 replaces the previous H2 and its H3 children.
    headings[:] = [(old_level, old_title) for old_level, old_title in headings if old_level < level]

    # Add the new heading.
    headings.append((level, title))

    # Build the full heading path.
    titles = []

    for _, heading_title in headings:
        titles.append(heading_title)

    return " > ".join(titles)


def _page_range(pages: list[int]) -> dict:
    """Return the first and last page numbers."""

    valid_pages = []

    for page in pages:
        if page is not None:
            valid_pages.append(page)

    if not valid_pages:
        return {}

    return {
        "page_start": min(valid_pages),
        "page_end": max(valid_pages),
    }


def merge_small_sections(
    sections: list[Document],
    min_tokens: int,
    max_tokens: int,
) -> list[Document]:
    """Merge small neighboring sections when allowed.

    Conditions:
    1. Both sections belong to the same document.
    2. Both share the same top-level heading.
    3. At least one section is smaller than min_tokens.
    4. Their combined size does not exceed max_tokens.
    """

    merged = []

    for section in sections:
        # The first section has no previous neighbor.
        if not merged:
            merged.append(section)
            continue

        previous = merged[-1]

        # Different document or top-level heading:
        # Don't merge these sections.
        if not same_group(previous, section):
            merged.append(section)
            continue

        previous_tokens = count_tokens(previous.content)
        current_tokens = count_tokens(section.content)

        # If both sections are large enough, keep them separate.
        if previous_tokens >= min_tokens and current_tokens >= min_tokens:
            merged.append(section)
            continue

        # Combine the text, keeping both section paths.
        combined_content = previous.content + "\n\n" + section.content

        # Don't merge if the result would exceed max_tokens.
        if count_tokens(combined_content) > max_tokens:
            merged.append(section)
            continue

        # Replace the previous section with the merged document.
        merged[-1] = Document(
            content=combined_content,
            meta=merged_meta(previous, section),
        )

    return merged


def same_group(first: Document, second: Document) -> bool:
    """Check whether two sections can belong to the same group."""

    # Sections must come from the same original document.
    if first.meta.get("document_id") != second.meta.get("document_id"):
        return False

    # Get the top-level heading for each section.
    first_path = first.meta.get("section_path") or ""
    second_path = second.meta.get("section_path") or ""

    first_top = first_path.split(" > ")[0]
    second_top = second_path.split(" > ")[0]

    return first_top == second_top


def merged_meta(first: Document, second: Document) -> dict:
    """Combine metadata and keep the shared heading path."""

    first_path = (first.meta.get("section_path") or "").split(" > ")

    second_path = (second.meta.get("section_path") or "").split(" > ")

    # Find the headings shared by both sections.
    shared = []

    for first_title, second_title in zip(
        first_path,
        second_path,
        strict=False,
    ):
        if first_title != second_title:
            break

        shared.append(first_title)

    # Collect page boundaries from both sections.
    pages = [
        first.meta.get("page_start"),
        first.meta.get("page_end"),
        second.meta.get("page_start"),
        second.meta.get("page_end"),
    ]

    return {
        **first.meta,
        "section_path": " > ".join(shared) or None,
        **_page_range(pages),
    }
