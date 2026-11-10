from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversations.schemas.message import (
    MessageBody,
    MessageContext,
    MessageResponse,
)
from app.conversations.schemas.thread import (
    ThreadListResponse,
    ThreadMessagesResponse,
    ThreadResponse,
    ThreadSummary,
)
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


@router.get("/threads", response_model=ThreadListResponse)
async def list_threads(
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ThreadListResponse:
    service = ConversationService(session)
    threads, has_more = await service.list_threads(limit, offset)

    return ThreadListResponse(
        threads=[ThreadSummary(thread_id=thread.id, title=thread.title) for thread in threads],
        has_more=has_more,
    )


@router.get(
    "/threads/{thread_id}/messages",
    response_model=ThreadMessagesResponse,
)
async def get_thread_messages(
    thread_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ThreadMessagesResponse:
    service = ConversationService(session)

    try:
        messages = await service.get_thread_messages(thread_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ThreadMessagesResponse(
        thread_id=thread_id,
        messages=[
            MessageResponse(
                context=MessageContext(
                    message_id=message.id,
                    interaction_id=message.interaction_id,
                    thread_id=message.thread_id,
                    role=message.role,
                ),
                body=MessageBody(
                    text=message.content,
                    entities=message.entities,
                ),
            )
            for message in messages
        ],
    )
