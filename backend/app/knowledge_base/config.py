from typing import Self

from pydantic import BaseModel, Field, model_validator


class KnowledgeBaseConfig(BaseModel):
    code: str
    name: str
    embedding_model: str = "text-embedding-3-small"
    max_chunk_tokens: int = Field(default=800, gt=0)
    # Sections smaller than this are joined with a neighbour (0 = never)
    min_chunk_tokens: int = Field(default=50, ge=0)
    # Sentences repeated at the start of the next chunk when a long paragraph is split
    chunk_overlap_sentences: int = Field(default=2, ge=0)

    @model_validator(mode="after")
    def validate_chunk_sizes(self) -> Self:
        if self.min_chunk_tokens >= self.max_chunk_tokens:
            raise ValueError("min_chunk_tokens must be smaller than max_chunk_tokens")
        return self
