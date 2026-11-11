from app.configurations.entities.registry import ENTITIES
from app.configurations.integrations.registry import INTEGRATIONS
from app.configurations.parameters import PARAMETERS
from app.configurations.schemas import APIIntegrationConfig
from app.configurations.tools.registry import TOOLS


# validate the relations
def validate_config() -> None:
    # Build configuration lookup dictionaries
    parameter_codes = {p.code for p in PARAMETERS}
    integrations_by_code = {i.code: i for i in INTEGRATIONS}
    entities_by_code = {e.code: e for e in ENTITIES}

    # Validate tool configurations
    for tool in TOOLS:
        referenced = tool.required_parameters + tool.optional_parameters

        for code in referenced:
            if code not in parameter_codes:
                raise ValueError(f"Tool '{tool.code}' references unknown parameter '{code}'")

        if set(tool.required_parameters) & set(tool.optional_parameters):
            raise ValueError(f"Tool '{tool.code}' has overlapping required and optional parameters")

        if not tool.integration_code:
            continue

        integration = integrations_by_code.get(tool.integration_code)

        if integration is None:
            raise ValueError(
                f"Tool '{tool.code}' references unknown integration '{tool.integration_code}'"
            )

        # Check required parameters against API mappings
        if isinstance(integration, APIIntegrationConfig):
            mapped_parameters = set(integration.query_params.values()) | set(
                integration.payload.values()
            )

            missing_mappings = set(tool.required_parameters) - mapped_parameters

            if missing_mappings:
                raise ValueError(
                    f"Tool '{tool.code}' has required parameters "
                    f"not mapped by integration '{integration.code}': "
                    f"{sorted(missing_mappings)}"
                )

            # Detect optional parameters that the integration doesn't consume
            unmapped_optional = set(tool.optional_parameters) - mapped_parameters

            if unmapped_optional:
                raise ValueError(
                    f"Tool '{tool.code}' has optional parameters "
                    f"not mapped by integration '{integration.code}': "
                    f"{sorted(unmapped_optional)}"
                )

    # Validate entity definitions
    for entity in ENTITIES:
        for code in entity.parameters:
            if code not in parameter_codes:
                raise ValueError(f"Entity '{entity.code}' references unknown parameter '{code}'")

        if (
            entity.identifier_parameter is not None
            and entity.identifier_parameter not in entity.parameters
        ):
            raise ValueError(f"Entity '{entity.code}' has an invalid identifier parameter")

        if entity.label_parameter is not None and entity.label_parameter not in entity.parameters:
            raise ValueError(f"Entity '{entity.code}' has an invalid label parameter")

        if not set(entity.brief_parameters) <= set(entity.parameters):
            raise ValueError(f"Entity '{entity.code}' has invalid brief parameters")

    # Validate integration configurations
    for integration in INTEGRATIONS:
        if not isinstance(integration, APIIntegrationConfig):
            continue

        # Validate API parameter references
        referenced = list(integration.query_params.values())
        referenced += list(integration.payload.values())

        for code in referenced:
            if code not in parameter_codes:
                raise ValueError(
                    f"Integration '{integration.code}' references unknown parameter '{code}'"
                )

        # Skip integrations without entity mapping
        if integration.entity_mapping is None:
            continue

        mapping = integration.entity_mapping

        if mapping.entity_code not in entities_by_code:
            raise ValueError(
                f"Integration '{integration.code}' references "
                f"unknown entity '{mapping.entity_code}'"
            )

        entity = entities_by_code[mapping.entity_code]

        # Validate entity field mappings
        for parameter_code in mapping.field_mapping:
            if parameter_code not in entity.parameters:
                raise ValueError(
                    f"Integration '{integration.code}' maps parameter "
                    f"'{parameter_code}' which is not defined "
                    f"in entity '{entity.code}'"
                )
