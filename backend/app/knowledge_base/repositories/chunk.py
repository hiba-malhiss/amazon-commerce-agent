from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.knowledge_base.models import KnowledgeChunk, KnowledgeDocument


class KnowledgeChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_all(self, chunks: Iterable[KnowledgeChunk]) -> None:
        self.session.add_all(chunks)
        await self.session.flush()

    async def list_by_document(self, document_id: UUID) -> list[KnowledgeChunk]:
        result = await self.session.scalars(
            select(KnowledgeChunk)
            .where(KnowledgeChunk.document_id == document_id)
            .order_by(KnowledgeChunk.chunk_index)
        )
        return list(result.all())

    async def delete_by_document(self, document_id: UUID) -> None:
        await self.session.execute(
            delete(KnowledgeChunk).where(KnowledgeChunk.document_id == document_id)
        )

    async def search(
        self, knowledge_base_code: str, embedding: list[float], limit: int
    ) -> list[tuple[KnowledgeChunk, str, float]]:
        """The closest chunks of `ready` documents: (chunk, filename, cosine distance)."""
        distance = KnowledgeChunk.embedding.cosine_distance(embedding)
        result = await self.session.execute(
            select(KnowledgeChunk, KnowledgeDocument.filename, distance)
            .join(KnowledgeDocument)
            .where(
                KnowledgeChunk.knowledge_base_code == knowledge_base_code,
                KnowledgeDocument.status == "ready",
            )
            .order_by(distance)
            .limit(limit)
        )
        return [(chunk, filename, row_distance) for chunk, filename, row_distance in result.all()]
