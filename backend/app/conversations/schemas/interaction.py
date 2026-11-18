from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.conversations.schemas.message import MessageResponse


class InteractionResponse(BaseModel):
    thread_id: UUID
    interaction_id: UUID
    user_message: MessageResponse
    assistant_message: MessageResponse | None = None


class InteractionEventsResponse(BaseModel):
    events: list[dict[str, Any]]
    prompts: list[dict[str, Any]] = []
