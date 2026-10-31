from typing import Any

from pydantic import BaseModel, Field


class Request(BaseModel):
    question: str
    tool: str
    entities: list[str] = Field(default_factory=list)


class UnderstandingResult(BaseModel):
    parameters: dict[str, Any] = Field(default_factory=dict)
    requests: list[Request] = Field(default_factory=list)
