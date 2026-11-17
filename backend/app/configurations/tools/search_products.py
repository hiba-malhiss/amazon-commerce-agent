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
        # "sort" removed for now: an API-side sort (e.g. cheapest first) on a broad keyword
        # surfaces irrelevant cheap accessories (a $3 "TV sticker" for "cheapest tv").
        # Re-enable only with relevance-aware sorting (sort the relevant results, not the API).
        "currency",
        "page",
    ],
    integration_code="amazon_product_search",
)
