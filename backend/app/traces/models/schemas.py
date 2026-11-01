from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TraceDecision(BaseModel):
    type: str
    status: str
    details: dict[str, Any] = Field(default_factory=dict)


class TraceInfo(BaseModel):
    interaction_id: UUID
    thread_id: UUID
    input: str

    # Agent state before the interaction
    context: dict[str, Any] = Field(default_factory=dict)

    # Understanding node output
    understanding: dict[str, Any] = Field(default_factory=dict)

    # Ordered execution events after understanding
    decisions: list[TraceDecision] = Field(default_factory=list)

    # Final assistant response
    response: dict[str, Any] = Field(default_factory=dict)

    latency_ms: float | None = None
