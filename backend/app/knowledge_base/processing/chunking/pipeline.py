import hashlib
from pathlib import Path

from haystack import Document

from app.configurations.schemas import KnowledgeBaseConfig
from app.knowledge_base.processing.converter import extract_document_content

from .paragraph import split_by_paragraph
from .structure import merge_small_sections, split_by_structure
from .tokens import count_tokens


def chunk_file(path: Path, document_id: str, config: KnowledgeBaseConfig) -> list[Document]:
    """Read a file and split it into chunks ready to embed."""

    return chunk_documents(extract_document_content(path, document_id, config.code), config)


def chunk_documents(documents: list[Document], config: KnowledgeBaseConfig) -> list[Document]:
    """Headings → sections, small sections joined, large ones split by paragraph (then
    sentence, then tokens). Each chunk gets a stable id, its position and its token count."""

    sections = split_by_structure(documents)
    sections = merge_small_sections(sections, config.min_chunk_tokens, config.max_chunk_tokens)

    chunks = []
    for section in sections:
        if count_tokens(section.content) <= config.max_chunk_tokens:
            chunks.append(section)
        else:
            chunks.extend(
                split_by_paragraph(section, config.max_chunk_tokens, config.chunk_overlap_sentences)
            )

    return [with_identity(chunk, index) for index, chunk in enumerate(chunks)]


def with_identity(chunk: Document, index: int) -> Document:
    """The chunk with a stable id: re-indexing the same file gives the same ids, so a
    retried job overwrites its own rows instead of duplicating them."""

    document_id = chunk.meta["document_id"]
    digest = hashlib.sha256(f"{document_id}:{index}:{chunk.content}".encode()).hexdigest()

    return Document(
        id=digest,
        content=chunk.content,
        meta={**chunk.meta, "chunk_index": index, "token_count": count_tokens(chunk.content)},
    )
