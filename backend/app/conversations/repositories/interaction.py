from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.conversations.models import Interaction


class InteractionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, thread_id: UUID) -> Interaction:
        # Create an interaction within a thread
        interaction = Interaction(thread_id=thread_id)

        self.session.add(interaction)
        await self.session.flush()

        return interaction

    async def get_by_id(self, interaction_id: UUID) -> Interaction | None:
        return await self.session.get(Interaction, interaction_id)
