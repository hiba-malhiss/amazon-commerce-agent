import logging
from pathlib import Path
from uuid import UUID

import openai
from haystack import Document
from sqlalchemy.ext.asyncio import AsyncSession

from app.configurations.knowledge_bases.registry import KNOWLEDGE_BASES_BY_CODE
from app.configurations.schemas import KnowledgeBaseConfig
from app.database.session import standalone_session
from app.knowledge_base.models import KnowledgeChunk, KnowledgeDocument
from app.knowledge_base.processing.chunking.pipeline import chunk_file
from app.knowledge_base.processing.embedding import embed_chunks
from app.knowledge_base.repositories import KnowledgeChunkRepository, KnowledgeDocumentRepository
from app.knowledge_base.services.events import publish_document_event

logger = logging.getLogger(__name__)

# Longest error message kept on a failed document
MAX_ERROR_LENGTH = 1000
RETRYABLE_ERRORS = (openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError)


class KnowledgeIndexer:
    """Turns a registered document's file into searchable chunks (run by the Celery worker)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.documents = KnowledgeDocumentRepository(session)
        self.chunks = KnowledgeChunkRepository(session)

    async def index_document(
        self, document: KnowledgeDocument, path: Path, config: KnowledgeBaseConfig
    ) -> None:
        """Chunk and embed the file, then in one transaction write its chunks, replace an
        older version of the same filename, and mark it `ready`: search never sees a
        half-indexed or doubled document. Errors are raised with nothing written; the
        caller decides whether to retry or `mark_failed`. A document deleted while it was
        being indexed is left deleted. Each step is published live to the page."""
        document_id = document.id  # still readable after a rollback expires the row
        try:
            await publish_document_event(document, step="chunking")
            chunks = chunk_file(path, str(document_id), config)
            await publish_document_event(document, step="embedding")
            chunks = await embed_chunks(chunks, config)

            if not await self.documents.exists(document_id):
                return

            # Chunks left by an earlier failed attempt, and older versions of this file
            await self.chunks.delete_by_document(document_id)
            await self.documents.delete_other_versions(document)
            await self.chunks.add_all(to_chunk_row(chunk, document, config) for chunk in chunks)
            document.status = "ready"
            document.error = None  # from a retried attempt
            document.chunk_count = len(chunks)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        await publish_document_event(document)

    async def mark_failed(self, document_id: UUID, error: Exception) -> None:
        """Save the error on the document as `failed` (unless it was deleted meanwhile)."""
        document = await self.documents.get_by_id(document_id)
        if document is None:
            return
        document.status = "failed"
        document.error = error_message(error)
        await self.session.commit()
        await publish_document_event(document)

    async def mark_retrying(self, document_id: UUID, error: Exception) -> None:
        """Save why the document will be indexed again (it stays `indexing`)."""
        document = await self.documents.get_by_id(document_id)
        if document is None:
            return
        document.error = error_message(error)
        await self.session.commit()
        await publish_document_event(document, step="retrying")


async def index_uploaded_document(
    document_id: UUID, path: Path, kb_code: str, *, final_attempt: bool
) -> None:
    """The worker's job: index a queued document, with its own database session.

    Retryable errors are raised again (the document stays `indexing`) so Celery retries
    later; on the final attempt, or any other error, the document is marked `failed`.
    Skipped when there's nothing to do: deleted, or done by an earlier run of this job.
    """
    async with standalone_session() as session:
        indexer = KnowledgeIndexer(session)
        document = await indexer.documents.get_by_id(document_id)
        if document is None or document.status != "indexing":
            return
        try:
            config = KNOWLEDGE_BASES_BY_CODE.get(kb_code)
            if config is None:
                raise ValueError(f"Unknown knowledge base: {kb_code}")
            await indexer.index_document(document, path, config)
        except RETRYABLE_ERRORS as error:
            if not final_attempt:
                logger.warning("Indexing document %s will be retried: %s", document_id, error)
                await indexer.mark_retrying(document_id, error)
                raise  # we need to rais the error so celery handle it
            await indexer.mark_failed(document_id, error)
            logger.exception("Indexing failed for document %s after retries", document_id)
        except Exception as error:
            await indexer.mark_failed(document_id, error)
            logger.exception("Indexing failed for document %s", document_id)


def error_message(error: Exception) -> str:
    return str(error)[:MAX_ERROR_LENGTH] or type(error).__name__


def to_chunk_row(
    chunk: Document, document: KnowledgeDocument, config: KnowledgeBaseConfig
) -> KnowledgeChunk:
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
