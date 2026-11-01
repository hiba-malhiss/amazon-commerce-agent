from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Trace(Base):
    __tablename__ = "traces"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    # One trace per interaction
    interaction_id: Mapped[UUID] = mapped_column(
        ForeignKey("interactions.id"),
        unique=True,
        nullable=False,
    )

    # Parent conversation
    thread_id: Mapped[UUID] = mapped_column(
        ForeignKey("threads.id"),
        nullable=False,
    )

    # Complete trace built after graph execution
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (Index("ix_traces_thread_id_created_at", "thread_id", "created_at"),)
