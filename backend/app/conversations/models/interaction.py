from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.conversations.models.message import Message
    from app.conversations.models.thread import Thread


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    # Parent conversation
    thread_id: Mapped[UUID] = mapped_column(
        ForeignKey("threads.id"),
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    messages: Mapped[list[Message]] = relationship(
        "Message",
        back_populates="interaction",
    )

    thread: Mapped[Thread] = relationship(
        "Thread",
        back_populates="interactions",
    )
