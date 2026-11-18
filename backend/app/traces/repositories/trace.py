from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.traces.models.trace import Trace


class TraceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, interaction_id: UUID, thread_id: UUID, data: dict) -> Trace:
        """Save one interaction's trace (events + prompts) for later debugging."""
        trace = Trace(interaction_id=interaction_id, thread_id=thread_id, data=data)
        self.session.add(trace)
        await self.session.flush()
        return trace

    async def get_by_interaction(self, interaction_id: UUID) -> Trace | None:
        return await self.session.scalar(
            select(Trace).where(Trace.interaction_id == interaction_id)
        )
