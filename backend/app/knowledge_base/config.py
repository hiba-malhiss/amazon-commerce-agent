from pydantic import BaseModel, Field


class KnowledgeBaseConfig(BaseModel):
    code: str
    name: str
    embedding_model: str = "text-embedding-3-small"
    max_chunk_tokens: int = Field(default=800, gt=0)
    # Sentences repeated at the start of the next chunk when a long paragraph is split
    chunk_overlap_sentences: int = Field(default=2, ge=0)
