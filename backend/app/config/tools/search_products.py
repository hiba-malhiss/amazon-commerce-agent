from app.schemas.config import ToolConfig

SEARCH_PRODUCTS = ToolConfig(
    code="search_products",
    name="Search Products",
    description="Search Amazon products matching user criteria",
    required_parameters=["query"],
    optional_parameters=[
        "brand",
        "category",
        "min_price",
        "max_price",
    ],
    integration_code="amazon_product_search",
)
