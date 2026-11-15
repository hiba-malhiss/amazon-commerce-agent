from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.knowledge_base.models import KnowledgeDocument


class KnowledgeDocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, document: KnowledgeDocument) -> KnowledgeDocument:
        self.session.add(document)
        await self.session.flush()
        return document

    async def get_by_id(self, document_id: UUID) -> KnowledgeDocument | None:
        return await self.session.get(KnowledgeDocument, document_id)

    async def get_by_sha256(
        self, knowledge_base_code: str, sha256: str
    ) -> KnowledgeDocument | None:
        return await self.session.scalar(
            select(KnowledgeDocument).where(
                KnowledgeDocument.knowledge_base_code == knowledge_base_code,
                KnowledgeDocument.sha256 == sha256,
            )
        )

    async def list_by_knowledge_base(self, knowledge_base_code: str) -> list[KnowledgeDocument]:
        result = await self.session.scalars(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.knowledge_base_code == knowledge_base_code)
            .order_by(KnowledgeDocument.created_at.desc(), KnowledgeDocument.id.desc())
        )
        return list(result.all())

    async def exists(self, document_id: UUID) -> bool:
        """Asked of the database, not the session's cache: the row may have been deleted."""
        found = await self.session.scalar(
            select(KnowledgeDocument.id).where(KnowledgeDocument.id == document_id)
        )
        return found is not None

    async def delete(self, document: KnowledgeDocument) -> None:
        await self.session.delete(document)
        await self.session.flush()

    async def delete_other_versions(self, document: KnowledgeDocument) -> None:
        """Older documents of the same filename in the same knowledge base."""
        await self.session.execute(
            delete(KnowledgeDocument).where(
                KnowledgeDocument.knowledge_base_code == document.knowledge_base_code,
                KnowledgeDocument.filename == document.filename,
                KnowledgeDocument.id != document.id,
            )
        )
