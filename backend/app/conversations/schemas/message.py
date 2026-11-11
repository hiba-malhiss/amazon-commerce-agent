from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, JsonValue


class MessageContext(BaseModel):
    message_id: UUID
    interaction_id: UUID
    thread_id: UUID
    role: Literal["user", "assistant"]


class Card(BaseModel):
    """One result shown under an assistant reply. "The second one" means number 2."""

    number: int
    reference: str
    entity_code: str
    label: str
    attributes: dict[str, JsonValue]


class MessageBody(BaseModel):
    text: str
    entities: list[Card] = Field(default_factory=list)  # the reply's cards, number 1 first


class MessageResponse(BaseModel):
    context: MessageContext
    body: MessageBody
