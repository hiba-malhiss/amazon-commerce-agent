from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversations.models import Thread


class ThreadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self) -> Thread:
        # Create a new conversation
        thread = Thread()

        self.session.add(thread)
        await self.session.flush()

        return thread

    async def get_by_id(self, thread_id: UUID) -> Thread | None:
        # Retrieve an existing conversation
        return await self.session.get(Thread, thread_id)

    async def list(self, limit: int, offset: int = 0) -> list[Thread]:
        query = (
            select(Thread)
            .order_by(Thread.created_at.desc(), Thread.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
