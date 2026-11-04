from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExtractedParameter(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    operation: Literal["set", "remove"] = "set"
    value: str | int | float | bool | None = None


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str
    tool: str
    entities: list[str] = Field(default_factory=list)
    parameters: list[ExtractedParameter] = Field(default_factory=list)
    relation: Literal["new", "follow_up", "ambiguous"] = "new"
    source_request_id: str | None = None


class UnderstandingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requests: list[Request]
    out_of_scope: bool = Field(
        default=False,
        description=(
            "True if the message asks for something no available tool can do "
            "False for greetings, thanks"
        )
    )
