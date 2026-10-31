from .product import PRODUCT

# Registered entity definitions
ENTITIES = [PRODUCT]

# Lookup entity definitions by code
ENTITIES_BY_CODE = {entity.code: entity for entity in ENTITIES}
