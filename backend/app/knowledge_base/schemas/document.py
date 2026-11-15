from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.knowledge_base.models import DocumentStatus


class KnowledgeDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    knowledge_base_code: str
    filename: str
    status: DocumentStatus
    error: str | None
    chunk_count: int
    created_at: datetime
    updated_at: datetime


class KnowledgeDocumentListResponse(BaseModel):
    documents: list[KnowledgeDocumentResponse]
