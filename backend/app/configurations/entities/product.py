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
        "rating",
        "review_count",
        "features",
    ],
    identifier_parameter="product_id",
    label_parameter="product_name",
    brief_parameters=["product_name", "brand", "price", "rating"],
)
