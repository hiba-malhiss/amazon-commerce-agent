from pydantic import BaseModel, ConfigDict


class KnowledgeChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chunk_index: int
    section_path: str | None
    page_start: int | None
    page_end: int | None
    token_count: int
    content: str


class KnowledgeChunkListResponse(BaseModel):
    chunks: list[KnowledgeChunkResponse]
