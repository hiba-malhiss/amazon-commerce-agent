from uuid import uuid4

from pydantic import BaseModel, Field

from app.agent.schemas.understanding import Request
from app.execution.schemas import ToolResult

ParameterValue = str | int | float | bool


class RequestExecution(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    request: Request
    parameters: dict[str, ParameterValue] = Field(default_factory=dict)
    step: str | None = None
    result: ToolResult | None = None
