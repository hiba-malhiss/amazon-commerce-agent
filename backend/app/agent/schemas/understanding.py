from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, create_model


class ExtractedParameter(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    operation: Literal["set", "remove"] = "set"
    value: str | int | float | bool | None = None


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str
    tool: str
    referenced_entities: list[str] = Field(
        default_factory=list,
        description="References of the visible results the user points at, if any.",
    )
    reference_quote: str | None = Field(
        default=None,
        description="The user's words that point at them, copied exactly from the message.",
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


def understanding_schema(references: list[str]) -> type[UnderstandingResult]:
    """UnderstandingResult whose referenced_entities can only be visible results."""
    if not references:
        return UnderstandingResult

    request = create_model(
        "Request",
        __base__=Request,
        referenced_entities=(
            list[Literal[tuple(references)]],
            Field(
                default_factory=list,
                description=Request.model_fields["referenced_entities"].description,
            ),
        ),
    )
    return create_model(
        "UnderstandingResult", __base__=UnderstandingResult, requests=(list[request], ...)
    )
