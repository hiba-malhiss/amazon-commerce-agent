from app.configurations.schemas import EntityConfig

PRODUCT = EntityConfig(
    code="product",
    name="Product",
    parameters=[
        "product_id",
        "product_name",
        "brand",
        "price",
        "currency",
    ],
    identifier_parameter="product_id",
)
