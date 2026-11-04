from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.settings import settings


class WebSocketChatRequest(BaseModel):
    type: Literal["message"] = "message"
    thread_id: UUID | None = None
    message: str = Field(
        min_length=1,
        max_length=settings.max_user_message_length,
    )
