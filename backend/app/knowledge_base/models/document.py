from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.knowledge_base.models.chunk import KnowledgeChunk

type DocumentStatus = Literal["indexing", "ready", "failed"]


class KnowledgeDocument(Base):
    """One indexed file. Its chunks are searchable only once it's `ready`."""

    __tablename__ = "knowledge_documents"
    # The same file is indexed once per knowledge base
    __table_args__ = (UniqueConstraint("knowledge_base_code", "sha256"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    knowledge_base_code: Mapped[str] = mapped_column(String(100), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    sha256: Mapped[str] = mapped_column(String(64))
    status: Mapped[DocumentStatus] = mapped_column(String(20), default="indexing")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    chunks: Mapped[list[KnowledgeChunk]] = relationship(
        back_populates="document", cascade="all, delete-orphan", passive_deletes=True
    )
