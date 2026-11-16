"""Convert a PDF into Markdown text for the knowledge base.

Steps:
1. Read PDF pages and extract text blocks and lines.
2. Keep each line's text, font size, bold status, and page number.
3. Detect headings using font information.
4. Clean the text and convert headings into Markdown (#, ##, etc.).
5. Return one Haystack Document with page information.

This module does NOT split text into chunks.
The chunker handles that separately.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pymupdf
from haystack import Document

from app.knowledge_base.processing import text_cleanup
from app.knowledge_base.processing.converters import pdf_headings

# PyMuPDF stores font properties as bit flags.
# Bit 4 indicates that the font is bold.
BOLD_FLAG = 1 << 4


@dataclass(frozen=True)
class _Line:
    """A single PDF text line and its formatting information."""

    text: str
    size: float
    bold: bool
    page: int


def convert_pdf(path: Path, metadata: dict[str, Any]) -> list[Document]:
    """Convert the entire PDF into one Haystack Document."""
    blocks = _read_blocks(path)

    # Collect font sizes to help detect headings.
    font_sizes = []

    for block in blocks:
        for line in block:
            font_sizes.append(line.size)

    heading_model = pdf_headings.build_model(font_sizes)

    # Convert lines into Markdown and track page numbers.
    content, line_pages = _render(blocks, heading_model)

    # Return PDF as one document
    if not content.strip():
        return []

    document_metadata = {
        **metadata,
        "line_pages": line_pages,
    }

    return [
        Document(
            content=content,
            meta=document_metadata,
        )
    ]


def _read_blocks(path: Path) -> list[list[_Line]]:
    """Read PDF pages and return groups of text lines.
    PDF structure:
        Page -> Blocks -> Lines -> Spans
    Each block contains a list of _Line objects.
    """

    blocks = []

    with pymupdf.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            # Extract blocks in approximate reading order.
            page_data = page.get_text("dict", sort=True)

            for block in page_data["blocks"]:
                lines = []

                # Image blocks usually have no "lines" field.
                for raw_line in block.get("lines", []):
                    line = _extract_line(raw_line, page_number)

                    if line is not None:
                        lines.append(line)

                if lines:
                    blocks.append(lines)

    return blocks


def _extract_line(raw_line: dict, page_number: int) -> _Line | None:
    """Extract text and formatting information from one PDF line."""

    # A line can contain multiple spans with different formatting.
    spans = raw_line.get("spans", [])

    # Combine all spans into one line of text.
    text_parts = []

    for span in spans:
        text_parts.append(span["text"])

    text = "".join(text_parts)

    text = text_cleanup.normalize_unicode(text).strip()

    if not text:
        return None

    # Use the largest font size found in this line.
    font_sizes = []

    for span in spans:
        font_sizes.append(span["size"])

    size = round(max(font_sizes), 1)

    # Check whether at least one span uses a bold font.
    bold = False

    for span in spans:
        has_bold_flag = bool(span["flags"] & BOLD_FLAG)
        has_bold_name = "bold" in span["font"].lower()

        if has_bold_flag or has_bold_name:
            bold = True
            break

    return _Line(
        text=text,
        size=size,
        bold=bold,
        page=page_number,
    )


def _render(
    blocks: list[list[_Line]],
    model: pdf_headings.HeadingModel,
) -> tuple[str, list[int]]:
    """Convert PDF lines into Markdown and track their page numbers.

    - Remove page headers, footers, and other detected page chrome.
    - Convert detected headings into Markdown headings.
    - Join words split across lines with a hyphen.
    - Separate text blocks with blank lines.
    """

    rendered = []
    pages = []

    for block in blocks:
        # Separate blocks with a blank line.
        # This helps the chunker preserve paragraph boundaries.
        if rendered:
            rendered.append("")
            pages.append(block[0].page)

        for line in block:
            # Skip repeated headers, footers, or page numbers
            if pdf_headings.is_chrome(line.text, line.size, model):
                continue

            heading_level = pdf_headings.heading_level(
                line.text,
                line.size,
                line.bold,
                model,
            )

            if heading_level:
                # Example: level 2 -> "## Shipping Policy"
                markdown_text = "#" * heading_level + " " + line.text

                rendered.append(markdown_text)
                pages.append(line.page)

            else:
                # Ordinary body text.
                _add_body_line(
                    rendered,
                    pages,
                    line.text,
                    line.page,
                )

    # Combine all lines into one Markdown string.
    markdown = "\n".join(rendered)

    return markdown, pages


def _add_body_line(
    rendered: list[str],
    pages: list[int],
    text: str,
    page: int,
) -> None:
    """Add body text, joining hyphenated words when possible."""

    # Only try joining if the previous line is body text.
    if _body_tail(rendered):
        # Example:
        # Previous: "The product is avail-"
        # Current:  "able now."
        # Result:   "The product is available now."
        joined = text_cleanup.join_hyphenated(
            rendered[-1],
            text,
        )

        if joined is not None:
            # Replace the previous line with the joined text.
            # No new page entry because no new line was added.
            rendered[-1] = joined
            return

    # Otherwise, add a new line and its page number.
    rendered.append(text)
    pages.append(page)


def _body_tail(rendered: list[str]) -> bool:
    """Check whether the previous rendered line is ordinary body text."""

    if not rendered:
        return False

    last_line = rendered[-1]

    if last_line == "":
        return False

    if last_line.startswith("#"):
        return False

    return True
