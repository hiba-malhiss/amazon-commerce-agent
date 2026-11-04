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
    entities: list[str] = Field(
        default_factory=list,
        description=(
            "References of known entities the user points at, e.g. 'product_B0CHR9K2LM'. "
            "Empty unless the user refers to a previous result. Never a product type or term."
        ),
    )
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
        ),
    )
    out_of_scope_reason: str | None = Field(
        default=None,
        description=(
            "Only when out_of_scope is true: the part that can't be done, in a few words "
            "(e.g. 'return policy question: no tool for store policies'). Otherwise null."
        ),
    )
