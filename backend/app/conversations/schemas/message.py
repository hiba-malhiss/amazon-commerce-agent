from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class MessageContext(BaseModel):
    message_id: UUID
    interaction_id: UUID
    thread_id: UUID
    role: Literal["user", "assistant"]


class MessageBody(BaseModel):
    text: str
    entities: list[str] = Field(default_factory=list)


class MessageResponse(BaseModel):
    context: MessageContext
    body: MessageBody
