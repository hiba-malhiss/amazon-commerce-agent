from uuid import UUID

from pydantic import BaseModel, Field

from app.conversations.schemas.message import MessageResponse


class ThreadResponse(BaseModel):
    thread_id: UUID


class ThreadSummary(BaseModel):
    thread_id: UUID
    title: str | None


class ThreadListResponse(BaseModel):
    threads: list[ThreadSummary] = Field(default_factory=list)


class ThreadMessagesResponse(BaseModel):
    thread_id: UUID
    messages: list[MessageResponse] = Field(default_factory=list)
