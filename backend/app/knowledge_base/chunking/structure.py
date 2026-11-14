import re

from haystack import Document

from .tokens import count_tokens


def split_by_structure(documents: list[Document]) -> list[Document]:
    """Split documents by Markdown headings while preserving section paths."""

    sections = []
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

    for document in documents:
        headings = []
        lines = []
        section_path = ""  # example: "Store Policies > Returns > Electronics"
        code_fence = None

        for line in (document.content or "").splitlines():
            marker = line.strip()[:3]

            # Don't interpret headings inside code blocks
            if marker in ("```", "~~~"):
                if code_fence is None:
                    code_fence = marker
                elif code_fence == marker:
                    code_fence = None

            match = heading_pattern.match(line) if code_fence is None else None

            if match:
                # save prev section and start a new one
                content = "\n".join(lines).strip()

                if content:
                    sections.append(
                        Document(
                            content=f"{section_path}\n\n{content}" if section_path else content,
                            meta={**document.meta, "section_path": section_path or None},
                        )
                    )

                # "### Electronics" => leve 3 , title Electronics
                level = len(match.group(1))
                title = match.group(2)

                headings = [(n, t) for n, t in headings if n < level]
                headings.append((level, title))

                section_path = " > ".join(t for _, t in headings)
                lines = []
            else:
                lines.append(line)

        # Save the final section
        content = "\n".join(lines).strip()

        if content:
            sections.append(
                Document(
                    content=f"{section_path}\n\n{content}" if section_path else content,
                    meta={**document.meta, "section_path": section_path or None},
                )
            )

    return sections


def merge_small_sections(
    sections: list[Document],
    min_tokens: int,
    max_tokens: int,
) -> list[Document]:
    """Join a section under min_tokens with its neighbour (forward, or backward for the last
    one) when both are in the same document and top-level section and the result fits in
    max_tokens. Each part keeps its own path in the text; nothing is dropped."""

    merged: list[Document] = []

    for section in sections:
        previous = merged[-1] if merged else None

        if (
            previous is not None
            and same_group(previous, section)
            and min(count_tokens(previous.content), count_tokens(section.content)) < min_tokens
        ):
            content = f"{previous.content}\n\n{section.content}"

            if count_tokens(content) <= max_tokens:
                merged[-1] = Document(content=content, meta=merged_meta(previous, section))
                continue

        merged.append(section)

    return merged


def same_group(first: Document, second: Document) -> bool:
    """Same document, and same top-level heading ("Returns" in "Returns > Electronics")."""

    def top_level(section: Document) -> str:
        return (section.meta.get("section_path") or "").split(" > ")[0]

    return first.meta.get("document_id") == second.meta.get("document_id") and top_level(
        first
    ) == top_level(second)


def merged_meta(first: Document, second: Document) -> dict:
    """The first part's metadata, with the path both share and pages covering both."""

    first_path = (first.meta.get("section_path") or "").split(" > ")
    second_path = (second.meta.get("section_path") or "").split(" > ")

    shared = []
    for a, b in zip(first_path, second_path, strict=False):
        if a != b:
            break
        shared.append(a)

    meta = {**first.meta, "section_path": " > ".join(shared) or None}
    if "page_end" in second.meta:
        meta["page_end"] = second.meta["page_end"]
    return meta
