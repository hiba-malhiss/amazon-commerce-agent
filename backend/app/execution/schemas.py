from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ToolResultStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    MISSING_PARAMETERS = "missing_parameters"


class ToolResult(BaseModel):
    # Errors are results, not exceptions, so one failed tool never breaks the graph
    status: ToolResultStatus
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    missing_parameters: list[str] = Field(default_factory=list)
