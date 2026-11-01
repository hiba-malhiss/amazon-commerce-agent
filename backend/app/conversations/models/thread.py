from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.conversations.models.interaction import Interaction


class Thread(Base):
    __tablename__ = "threads"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    interactions: Mapped[list[Interaction]] = relationship(
        "Interaction",
        back_populates="thread",
    )
