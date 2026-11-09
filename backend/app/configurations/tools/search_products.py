from app.configurations.schemas import ToolConfig

SEARCH_PRODUCTS = ToolConfig(
    code="search_products",
    name="Search Products",
    description="Search Amazon products by product name ex: TV",
    required_parameters=["product_name"],
    optional_parameters=[
        #         "brand",
        #         "category",
        "min_price",
        "max_price",
        "currency",
        "page",
    ],
    integration_code="amazon_product_search",
)
