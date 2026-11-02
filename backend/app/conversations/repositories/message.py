from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversations.models import Message


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        thread_id: UUID,
        interaction_id: UUID,
        role: str,
        content: str,
        entities: list[str] | None = None,
    ) -> Message:
        # Save message under its thread and interaction
        message = Message(
            thread_id=thread_id,
            interaction_id=interaction_id,
            role=role,
            content=content,
            entities=entities or [],
        )

        self.session.add(message)
        await self.session.flush()

        return message

    async def get_by_thread(
        self,
        thread_id: UUID,
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at, Message.id)
        )

        result = await self.session.execute(statement)
        return list(result.scalars().all())
