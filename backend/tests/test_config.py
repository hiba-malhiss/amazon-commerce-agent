import pytest
from pydantic import ValidationError

from app.configurations.schemas import APIIntegrationConfig, ParameterConfig
from app.configurations.validator import validate_config


def test_configuration_references():
    # Validate all registered configuration relationships
    validate_config()


def test_parameter_schema():
    parameter = ParameterConfig(
        code="query",
        name="Search Query",
        type="string",
        description="Product search query",
    )

    assert parameter.code == "query"


def test_invalid_parameter_type():
    # Reject unsupported parameter types
    with pytest.raises(ValidationError):
        ParameterConfig(
            code="query",
            name="Search Query",
            type="invalid",
            description="Product search query",
        )


def test_api_integration_schema():
    integration = APIIntegrationConfig(
        code="test_api",
        name="Test API",
        description="Example integration",
        url="https://example.com/api",
        method="GET",
    )

    assert integration.type == "api"
