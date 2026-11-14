import re

from haystack import Document


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
