from app.configurations.schemas import ToolConfig

PRODUCT_DETAILS = ToolConfig(
    code="product_details",
    name="Product Details",
    description=(
        "Get one product's full details (price, rating, review count, key features) by its "
        "product_id. Use it to answer questions about a product, and to compare products: "
        "one request per product."
    ),
    required_parameters=["product_id"],
    optional_parameters=["currency"],
    integration_code="amazon_product_details",
)
