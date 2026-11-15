from pathlib import Path

from haystack import Document
from sqlalchemy.ext.asyncio import AsyncSession

from app.configurations.schemas import KnowledgeBaseConfig
from app.knowledge_base.models import KnowledgeChunk, KnowledgeDocument
from app.knowledge_base.processing.chunking.pipeline import chunk_file
from app.knowledge_base.processing.embedding import embed_chunks
from app.knowledge_base.repositories import KnowledgeChunkRepository, KnowledgeDocumentRepository

# Longest error message kept on a failed document
MAX_ERROR_LENGTH = 1000


class KnowledgeIndexer:
    """Takes uploaded files to searchable chunks: used by the upload API, and later the
    background worker."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.documents = KnowledgeDocumentRepository(session)
        self.chunks = KnowledgeChunkRepository(session)

    async def register_document(
        self, filename: str, sha256: str, config: KnowledgeBaseConfig
    ) -> tuple[KnowledgeDocument, bool]:
        """The document row for this content, and whether it still needs indexing.

        Content already `ready` in this knowledge base (same SHA-256) is reused as it is;
        otherwise the row is created (or a failed one reused) and saved as `indexing`.
        """
        document = await self.documents.get_by_sha256(config.code, sha256)
        if document is not None and document.status == "ready":
            return document, False

        if document is None:
            document = await self.documents.add(
                KnowledgeDocument(knowledge_base_code=config.code, filename=filename, sha256=sha256)
            )
        document.status = "indexing"
        document.error = None
        await self.session.commit()
        return document, True

    async def index_document(
        self, document: KnowledgeDocument, path: Path, config: KnowledgeBaseConfig
    ) -> KnowledgeDocument:
        """Chunk and embed the file, then in one transaction write its chunks, replace an
        older version of the same filename, and mark it `ready`: search never sees a
        half-indexed or doubled document. Any error marks it `failed` and is raised again.
        A document deleted while it was being indexed is left deleted."""
        try:
            chunks = await embed_chunks(chunk_file(path, str(document.id), config), config)

            if not await self.documents.exists(document.id):
                return document

            # Chunks left by an earlier failed attempt, and older versions of this file
            await self.chunks.delete_by_document(document.id)
            await self.documents.delete_other_versions(document)
            await self.chunks.add_all(to_chunk_row(chunk, document, config) for chunk in chunks)
            document.status = "ready"
            document.chunk_count = len(chunks)
            await self.session.commit()

        except Exception as error:
            await self.session.rollback()
            if not await self.documents.exists(document.id):
                return document
            document.status = "failed"
            document.error = str(error)[:MAX_ERROR_LENGTH]
            await self.session.commit()
            raise

        return document


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
