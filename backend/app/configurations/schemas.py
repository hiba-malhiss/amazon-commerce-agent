from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator

ParameterCode = Annotated[
    str,
    Field(description="Reference to ParameterConfig.code"),
]

ToolCode = Annotated[
    str,
    Field(description="Reference to ToolConfig.code"),
]

IntegrationCode = Annotated[
    str,
    Field(description="Reference to IntegrationConfig.code"),
]

EntityCode = Annotated[
    str,
    Field(description="Reference to EntityConfig.code"),
]


class ParameterConfig(BaseModel):
    code: str
    name: str
    type: Literal["string", "number", "boolean"]
    description: str


class ToolConfig(BaseModel):
    code: str
    name: str
    description: str
    required_parameters: list[ParameterCode] = Field(default_factory=list)
    optional_parameters: list[ParameterCode] = Field(default_factory=list)
    integration_code: IntegrationCode | None = None


class IntegrationConfig(BaseModel):
    code: str
    name: str
    description: str


class EntityMappingConfig(BaseModel):
    entity_code: EntityCode
    # Path to the entity list in the API response
    collection_path: str
    # Entity parameter code -> API response field path
    field_mapping: dict[ParameterCode, str] = Field(default_factory=dict)



class AuthenticationConfig(BaseModel):
    type: Literal["none", "api_key", "basic"] = "none"

    # API key authentication
    key_name: str | None = None
    key_location: Literal["header", "query"] = "header"
    key_prefix: str = ""
    api_key_env: str | None = None

    # Basic authentication
    username_env: str | None = None
    password_env: str | None = None

    @model_validator(mode="after")
    def validate_auth(self) -> Self:
        if self.type == "api_key":
            if not self.key_name or not self.api_key_env:
                raise ValueError(
                    "API key authentication requires "
                    "key_name and api_key_env"
                )

        elif self.type == "basic":
            if not self.username_env or not self.password_env:
                raise ValueError(
                    "Basic authentication requires "
                    "username_env and password_env"
                )

        return self

# HTTP API integration
class APIIntegrationConfig(IntegrationConfig):
    type: Literal["api"] = "api"
    url: str
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "GET"
    headers: dict[str, str] = Field(default_factory=dict)
    static_query_params: dict[str, str] = Field(default_factory=dict)
    query_params: dict[str, ParameterCode] = Field(default_factory=dict)
    payload: dict[str, ParameterCode] = Field(default_factory=dict)
    entity_mapping: EntityMappingConfig | None = None
    authentication: AuthenticationConfig = Field(default_factory=AuthenticationConfig)


class EntityConfig(BaseModel):
    code: str
    name: str
    parameters: list[ParameterCode] = Field(default_factory=list)
    identifier_parameter: ParameterCode | None = None
