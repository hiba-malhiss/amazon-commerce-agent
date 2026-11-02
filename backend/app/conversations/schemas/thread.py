from uuid import UUID

from pydantic import BaseModel, Field

from app.conversations.schemas.message import MessageResponse


class ThreadResponse(BaseModel):
    thread_id: UUID


class ThreadMessagesResponse(BaseModel):
    thread_id: UUID
    messages: list[MessageResponse] = Field(default_factory=list)
