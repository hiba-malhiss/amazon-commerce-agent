from typing import Any
from uuid import uuid4

from app.configurations.entities.registry import ENTITIES_BY_CODE
from app.configurations.schemas import EntityMappingConfig


def get_path(data: dict, path: str) -> Any:
    # Read nested API response fields
    value = data

    for key in path.split("."):
        if not isinstance(value, dict):
            return None

        value = value.get(key)

    return value


def map_entities(
    response: dict[str, Any],
    mapping: EntityMappingConfig,
) -> list[dict[str, Any]]:
    entity_config = ENTITIES_BY_CODE[mapping.entity_code]

    items = get_path(response, mapping.collection_path)

    if not isinstance(items, list):
        return []

    entities = []

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue

        # Map API fields to entity parameters
        attributes = {code: get_path(item, path) for code, path in mapping.field_mapping.items()}

        # Use the configured identifier when available
        identifier = (
            attributes.get(entity_config.identifier_parameter)
            if entity_config.identifier_parameter
            else None
        )

        if identifier is None or identifier == "":
            identifier = uuid4().hex

        entities.append(
            {
                "reference": f"{entity_config.code}_{identifier}",
                "position": index + 1,
                "entity_code": entity_config.code,
                "attributes": attributes,
            }
        )

    return entities
