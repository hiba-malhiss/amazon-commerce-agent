from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class WebSocketChatRequest(BaseModel):
    type: Literal["message"] = "message"
    thread_id: UUID | None = None
    message: str
