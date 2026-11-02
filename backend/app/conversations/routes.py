from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversations.schemas.thread import ThreadResponse
from app.conversations.service import ConversationService
from app.database.session import get_db

router = APIRouter(tags=["Conversations"])


@router.post("/threads", response_model=ThreadResponse)
async def create_thread(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ThreadResponse:
    service = ConversationService(session)
    thread = await service.get_or_create_thread()

    return ThreadResponse(thread_id=thread.id)
