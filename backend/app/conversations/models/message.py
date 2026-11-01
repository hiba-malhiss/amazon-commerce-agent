from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.conversations.models.interaction import Interaction


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    # Parent interaction
    interaction_id: Mapped[UUID] = mapped_column(
        ForeignKey("interactions.id"),
        index=True,
    )

    role: Mapped[Literal["user", "assistant"]] = mapped_column(
        String(20),
    )

    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # extract from trace these are the id's
    entities: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    interaction: Mapped[Interaction] = relationship(
        "Interaction",
        back_populates="messages",
    )
