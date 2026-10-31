from pydantic import BaseModel, ConfigDict


class ExtractedParameter(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    value: str | float | bool


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str
    tool: str
    entities: list[str]


class UnderstandingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    parameters: list[ExtractedParameter]
    requests: list[Request]
