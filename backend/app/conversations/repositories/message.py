from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.conversations.models import Message


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        interaction_id: UUID,
        role: str,
        content: str,
        entities: list[str] | None = None,
    ) -> Message:
        # Store a message linked to an interaction
        message = Message(
            interaction_id=interaction_id,
            role=role,
            content=content,
            entities=entities or [],
        )

        self.session.add(message)
        await self.session.flush()

        return message
