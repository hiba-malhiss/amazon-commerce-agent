from app.configurations.schemas import ToolConfig
from app.execution.schemas import ParameterValue


def get_missing_parameters(
    tool: ToolConfig,
    parameters: dict[str, ParameterValue],
) -> list[str]:
    # Find required parameters with missing values
    return [
        code
        for code in tool.required_parameters
        if code not in parameters or parameters[code] is None
    ]
