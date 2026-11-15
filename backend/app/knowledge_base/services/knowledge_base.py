import asyncio
import hashlib
import logging
from pathlib import Path
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.configurations.knowledge_bases.registry import KNOWLEDGE_BASES, KNOWLEDGE_BASES_BY_CODE
from app.configurations.schemas import KnowledgeBaseConfig
from app.core.settings import settings
from app.knowledge_base.exceptions import (
    FileTooLargeError,
    IndexingUnavailableError,
    KnowledgeBaseError,
    NotFoundError,
)
from app.knowledge_base.models import KnowledgeChunk, KnowledgeDocument
from app.knowledge_base.processing.converter import SUPPORTED_SUFFIXES
from app.knowledge_base.repositories import KnowledgeChunkRepository, KnowledgeDocumentRepository
from app.knowledge_base.services.indexing import KnowledgeIndexer
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

# The Celery task that indexes an upload (app/knowledge_base/tasks.py), queued by name
INDEX_DOCUMENT_TASK = "knowledge_base.index_document"


class KnowledgeBaseService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.documents = KnowledgeDocumentRepository(session)
        self.chunks = KnowledgeChunkRepository(session)
        self.indexer = KnowledgeIndexer(session)

    def list_knowledge_bases(self) -> list[KnowledgeBaseConfig]:
        return KNOWLEDGE_BASES

    async def list_documents(self, kb_code: str) -> list[KnowledgeDocument]:
        config = knowledge_base(kb_code)
        return await self.documents.list_by_knowledge_base(config.code)

    async def list_chunks(self, kb_code: str, document_id: UUID) -> list[KnowledgeChunk]:
        """A document's chunks in order, as they were indexed (empty until it's `ready`)."""
        await self.get_document(kb_code, document_id)
        return await self.chunks.list_by_document(document_id)

    async def get_document(self, kb_code: str, document_id: UUID) -> KnowledgeDocument:
        config = knowledge_base(kb_code)
        document = await self.documents.get_by_id(document_id)
        if document is None or document.knowledge_base_code != config.code:
            raise NotFoundError("Document not found")
        return document

    async def upload_document(
        self, kb_code: str, filename: str, content: bytes
    ) -> KnowledgeDocument:
        """Check and save the file, save its document row, and queue its indexing.

        The document comes back `indexing` (the worker updates it), or `ready` when the same
        content is already indexed.
        """
        config = knowledge_base(kb_code)
        filename = Path(filename).name
        suffix = Path(filename).suffix.lower()

        if suffix not in SUPPORTED_SUFFIXES:
            raise KnowledgeBaseError(f"Supported files: {', '.join(sorted(SUPPORTED_SUFFIXES))}")
        if not content:
            raise KnowledgeBaseError("The file is empty")
        if len(content) > settings.max_upload_mb * 1024 * 1024:
            raise FileTooLargeError(f"Files can be at most {settings.max_upload_mb} MB")

        sha256 = hashlib.sha256(content).hexdigest()
        path = stored_file(config, sha256, suffix)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

        # Same content already indexed in this knowledge base: reuse it as it is
        document = await self.documents.get_by_sha256(config.code, sha256)
        if document is not None and document.status == "ready":
            return document

        # Otherwise create the row (or reuse a failed one) and save it as `indexing`
        if document is None:
            document = await self.documents.add(
                KnowledgeDocument(knowledge_base_code=config.code, filename=filename, sha256=sha256)
            )
        document.status = "indexing"
        document.error = None
        await self.session.commit()

        await self.queue_indexing(document, path, config)
        return document

    async def queue_indexing(
        self, document: KnowledgeDocument, path: Path, config: KnowledgeBaseConfig
    ) -> None:
        """Hand the document to the Celery worker. If the queue can't be reached, the
        document is marked `failed` (not left `indexing` forever) and can be uploaded again."""
        try:
            # Publishing blocks while it retries an unreachable Redis: keep it off the event loop
            await asyncio.to_thread(
                celery_app.send_task,
                INDEX_DOCUMENT_TASK,
                args=[str(document.id), str(path.resolve()), config.code],
            )
        except Exception as error:
            logger.exception("Couldn't queue indexing for document %s", document.id)
            await self.indexer.mark_failed(document.id, error)
            raise IndexingUnavailableError("Indexing is unavailable, try again later") from error

    async def delete_document(self, kb_code: str, document_id: UUID) -> None:
        """Delete the document, its chunks, and its file. Safe while it's being indexed: the
        indexing stops without writing anything."""
        config = knowledge_base(kb_code)
        document = await self.get_document(kb_code, document_id)

        path = stored_file(config, document.sha256, Path(document.filename).suffix.lower())
        await self.documents.delete(document)
        await self.session.commit()
        path.unlink(missing_ok=True)


def knowledge_base(code: str) -> KnowledgeBaseConfig:
    config = KNOWLEDGE_BASES_BY_CODE.get(code)
    if config is None:
        raise NotFoundError("Knowledge base not found")
    return config


def stored_file(config: KnowledgeBaseConfig, sha256: str, suffix: str) -> Path:
    """Where an uploaded file is kept: one file per content, so duplicates share it."""
    return settings.knowledge_storage_dir / config.code / f"{sha256}{suffix}"
