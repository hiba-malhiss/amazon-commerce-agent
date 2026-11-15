import re

from haystack import Document

from .tokens import count_tokens, encoding

# Tokens a window repeats from the previous one when text is cut by tokens
OVERLAP_TOKENS = 50


def split_by_paragraph(
    section: Document,
    max_tokens: int,
    overlap_sentences: int = 2,
) -> list[Document]:
    """Group paragraphs and split oversized ones into sentences."""

    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")

    if overlap_sentences < 0:
        raise ValueError("overlap_sentences cannot be negative")

    path = section.meta.get("section_path") or ""
    prefix = f"{path}\n\n" if path else ""

    text = section.content or ""

    # Remove the section path already added by structural splitting
    if prefix and text.startswith(prefix):
        text = text[len(prefix) :]

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks = []
    current = []

    for paragraph in paragraphs:
        candidate = "\n\n".join([*current, paragraph])

        if count_tokens(prefix + candidate) <= max_tokens:
            current.append(paragraph)
            continue

        # Save the current chunk before starting a new one
        if current:
            chunks.append(
                Document(
                    content=prefix + "\n\n".join(current),
                    meta=section.meta.copy(),
                )
            )
            current = []

        # The paragraph fits by itself
        if count_tokens(prefix + paragraph) <= max_tokens:
            current.append(paragraph)
            continue

        # Long paragraph: sentence splitting with overlap
        chunks.extend(
            split_long_paragraph(
                paragraph=paragraph,
                prefix=prefix,
                max_tokens=max_tokens,
                meta=section.meta,
                overlap_sentences=overlap_sentences,
            )
        )

    # Save the final chunk
    if current:
        chunks.append(
            Document(
                content=prefix + "\n\n".join(current),
                meta=section.meta.copy(),
            )
        )

    return chunks


SENTENCE_END = re.compile(r"(?<=[.!?؟])\s+|\n+")


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences. Plain regex: no model or download, same result every run."""

    return [sentence.strip() for sentence in SENTENCE_END.split(text) if sentence.strip()]


def split_long_paragraph(
    paragraph: str,
    prefix: str,
    max_tokens: int,
    meta: dict,
    overlap_sentences: int = 2,
) -> list[Document]:
    """Split a long paragraph into sentence groups with overlap."""

    sentences = split_into_sentences(paragraph)

    if not sentences and paragraph.strip():
        raise ValueError("Could not split the paragraph into sentences")

    chunks = []
    current = []

    for sentence in sentences:
        # One sentence too long for a chunk (a PDF line or list with no full stops):
        # save what's collected, then cut the sentence into token windows
        if count_tokens(prefix + sentence) > max_tokens:
            if current:
                chunks.append(Document(content=prefix + " ".join(current), meta=meta.copy()))
                current = []
            chunks.extend(split_by_tokens(sentence, prefix, max_tokens, meta))
            continue

        candidate = " ".join([*current, sentence])

        if count_tokens(prefix + candidate) <= max_tokens:
            current.append(sentence)
            continue

        # Save the full current chunk
        chunks.append(
            Document(
                content=prefix + " ".join(current),
                meta=meta.copy(),
            )
        )

        # Keep the last N sentences for overlap
        overlap_count = min(overlap_sentences, len(current))

        # Reduce overlap if it doesn't fit with the next sentence
        while overlap_count > 0:
            retained = current[-overlap_count:]
            candidate = " ".join([*retained, sentence])

            if count_tokens(prefix + candidate) <= max_tokens:
                break

            overlap_count -= 1

        current = current[-overlap_count:] if overlap_count else []
        current.append(sentence)

    # Save the last chunk
    if current:
        chunks.append(
            Document(
                content=prefix + " ".join(current),
                meta=meta.copy(),
            )
        )

    return chunks


def split_by_tokens(
    text: str,
    prefix: str,
    max_tokens: int,
    meta: dict,
    overlap_tokens: int = OVERLAP_TOKENS,
) -> list[Document]:
    """Last resort for text with no sentence breaks: cut it into windows of tokens, each
    repeating the end of the previous one (at most a quarter of a window)."""

    room = max_tokens - count_tokens(prefix)
    if room <= 0:
        raise ValueError("The section path alone exceeds max_tokens")

    overlap = min(overlap_tokens, room // 4)
    step = room - overlap
    tokens = encoding.encode(text)

    return [
        Document(content=prefix + encoding.decode(tokens[start : start + room]), meta=meta.copy())
        for start in range(0, max(len(tokens) - overlap, 1), step)
    ]
