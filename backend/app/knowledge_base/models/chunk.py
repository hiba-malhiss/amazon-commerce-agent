from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.knowledge_base.models.document import KnowledgeDocument

# Vector size of the embedding model (text-embedding-3-small). A model with another size
# needs a migration and a full re-index: vectors of different models can't be compared.
EMBEDDING_DIMENSIONS = 1536


class KnowledgeChunk(Base):
    """One searchable piece of a document, with its embedding."""

    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        # Fast approximate nearest-neighbour search by cosine distance
        Index(
            "ix_knowledge_chunks_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    # The pipeline's stable id (sha256 of document, position and content)
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"), index=True
    )
    # Copied from the document so a search filters chunks without a join
    knowledge_base_code: Mapped[str] = mapped_column(String(100), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    section_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_count: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSIONS))

    document: Mapped[KnowledgeDocument] = relationship(back_populates="chunks")
