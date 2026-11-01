from typing import Any

from app.configurations.schemas import ToolConfig


def get_missing_parameters(
    tool: ToolConfig,
    parameters: dict[str, Any],
) -> list[str]:
    # Find required parameters with missing values
    return [
        code
        for code in tool.required_parameters
        if code not in parameters or parameters[code] is None
    ]
