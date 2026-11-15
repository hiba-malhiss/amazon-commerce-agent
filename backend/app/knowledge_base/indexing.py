import hashlib
from pathlib import Path

from haystack import Document
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.knowledge_base.chunking.pipeline import chunk_file
from app.knowledge_base.config import KnowledgeBaseConfig
from app.knowledge_base.embedding import embed_chunks
from app.knowledge_base.models import KnowledgeChunk, KnowledgeDocument

# Longest error message kept on a failed document
MAX_ERROR_LENGTH = 1000


async def index_file(
    session: AsyncSession, path: Path, config: KnowledgeBaseConfig
) -> KnowledgeDocument:
    """Take one file to searchable chunks in the database.

    1. Same content already `ready` in this knowledge base (by SHA-256): nothing to do.
    2. The document is saved as `indexing`.
    3. The file is chunked and embedded.
    4. One transaction writes its chunks, replaces an older version of the same filename,
       and marks it `ready`: search never sees a half-indexed or doubled document.
    5. On any error it's marked `failed` with the error, and the error is raised again.
    """
    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()

    document = await session.scalar(
        select(KnowledgeDocument).where(
            KnowledgeDocument.knowledge_base_code == config.code,
            KnowledgeDocument.sha256 == sha256,
        )
    )
    if document is not None and document.status == "ready":
        return document

    if document is None:
        document = KnowledgeDocument(
            knowledge_base_code=config.code, filename=path.name, sha256=sha256
        )
        session.add(document)
    document.status = "indexing"
    document.error = None
    await session.commit()

    try:
        chunks = await embed_chunks(chunk_file(path, str(document.id), config), config)

        # Chunks left by an earlier failed attempt, and older versions of this file
        await session.execute(
            delete(KnowledgeChunk).where(KnowledgeChunk.document_id == document.id)
        )
        await session.execute(
            delete(KnowledgeDocument).where(
                KnowledgeDocument.knowledge_base_code == config.code,
                KnowledgeDocument.filename == path.name,
                KnowledgeDocument.id != document.id,
            )
        )
        session.add_all(to_chunk_row(chunk, document, config) for chunk in chunks)
        document.status = "ready"
        document.chunk_count = len(chunks)
        await session.commit()

    except Exception as error:
        await session.rollback()
        document.status = "failed"
        document.error = str(error)[:MAX_ERROR_LENGTH]
        await session.commit()
        raise

    return document


def to_chunk_row(chunk: Document, document: KnowledgeDocument, config: KnowledgeBaseConfig):
    return KnowledgeChunk(
        id=chunk.id,
        document_id=document.id,
        knowledge_base_code=config.code,
        chunk_index=chunk.meta["chunk_index"],
        content=chunk.content,
        section_path=chunk.meta.get("section_path"),
        page_start=chunk.meta.get("page_start"),
        page_end=chunk.meta.get("page_end"),
        token_count=chunk.meta["token_count"],
        embedding=chunk.embedding,
    )
