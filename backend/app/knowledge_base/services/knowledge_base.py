import hashlib
import logging
from pathlib import Path
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.configurations.knowledge_bases.registry import KNOWLEDGE_BASES, KNOWLEDGE_BASES_BY_CODE
from app.configurations.schemas import KnowledgeBaseConfig
from app.core.settings import settings
from app.database.session import AsyncSessionLocal
from app.knowledge_base.exceptions import FileTooLargeError, KnowledgeBaseError, NotFoundError
from app.knowledge_base.models import KnowledgeChunk, KnowledgeDocument
from app.knowledge_base.processing.converter import SUPPORTED_SUFFIXES
from app.knowledge_base.repositories import KnowledgeChunkRepository, KnowledgeDocumentRepository
from app.knowledge_base.services.indexing import KnowledgeIndexer

logger = logging.getLogger(__name__)


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
    ) -> tuple[KnowledgeDocument, Path | None]:
        """Check and save the file, and register its document.

        Returns the document, and the saved file when it still needs indexing (None when
        the same content is already `ready`).
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

        document, needs_indexing = await self.indexer.register_document(filename, sha256, config)
        return document, path if needs_indexing else None

    async def delete_document(self, kb_code: str, document_id: UUID) -> None:
        """Delete the document, its chunks, and its file. Safe while it's being indexed: the
        indexing stops without writing anything."""
        config = knowledge_base(kb_code)
        document = await self.get_document(kb_code, document_id)

        path = stored_file(config, document.sha256, Path(document.filename).suffix.lower())
        await self.documents.delete(document)
        await self.session.commit()
        path.unlink(missing_ok=True)


async def index_in_background(document_id: UUID, path: Path, kb_code: str) -> None:
    """Index an uploaded document after the response, with its own database session."""
    async with AsyncSessionLocal() as session:
        document = await KnowledgeDocumentRepository(session).get_by_id(document_id)
        if document is None:
            return
        try:
            await KnowledgeIndexer(session).index_document(document, path, knowledge_base(kb_code))
        except Exception:
            # Already saved on the document as `failed` with the error
            logger.exception("Indexing failed for document %s", document_id)


def knowledge_base(code: str) -> KnowledgeBaseConfig:
    config = KNOWLEDGE_BASES_BY_CODE.get(code)
    if config is None:
        raise NotFoundError("Knowledge base not found")
    return config


def stored_file(config: KnowledgeBaseConfig, sha256: str, suffix: str) -> Path:
    """Where an uploaded file is kept: one file per content, so duplicates share it."""
    return settings.knowledge_storage_dir / config.code / f"{sha256}{suffix}"
