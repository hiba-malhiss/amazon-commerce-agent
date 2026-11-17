from app.configurations.schemas import ParameterConfig

PARAMETERS = [
    ParameterConfig(
        code="brand",
        name="Brand",
        type="string",
        description="Product brand",
    ),
    ParameterConfig(
        code="category",
        name="Category",
        type="string",
        description=(
            "Broad shopping department, only when the user names one or it is obvious. "
            "Never the product type itself: 'tv' or 'headphones' are not categories "
            "(a TV is in 'electronics')."
        ),
    ),
    ParameterConfig(
        code="min_price",
        name="Minimum Price",
        type="number",
        description="Minimum product price",
    ),
    ParameterConfig(
        code="max_price",
        name="Maximum Price",
        type="number",
        description="Maximum product price",
    ),
    ParameterConfig(
        code="product_id",
        name="Product ID",
        type="string",
        description="Unique product identifier from the provider",
    ),
    ParameterConfig(
        code="product_name",
        name="Product Name",
        type="string",
        description="Product title or name",
    ),
    ParameterConfig(
        code="price",
        name="Price",
        type="number",
        description="Product price",
    ),
    ParameterConfig(
        code="currency",
        name="Currency",
        type="string",
        description="Currency used for product prices",
    ),
    ParameterConfig(
        code="page",
        name="Page",
        type="number",
        description=(
            "Results page number, starting at 1. When the user asks for more options, "
            "set it to the previous request's page + 1"
        ),
    ),
    ParameterConfig(
        code="rating",
        name="Rating",
        type="number",
        description="Average customer rating, out of 5",
    ),
    ParameterConfig(
        code="review_count",
        name="Review Count",
        type="number",
        description="Number of customer ratings",
    ),
    ParameterConfig(
        code="image",
        name="Image",
        type="string",
        description="URL of the product's image",
    ),
    ParameterConfig(
        code="link",
        name="Link",
        type="string",
        description="URL of the product's page",
    ),
    ParameterConfig(
        code="features",
        name="Features",
        type="list",
        description="Key feature bullet points of a product",
    ),
    #     ParameterConfig(
    #         code="sort",
    #         name="Sort order",
    #         type="string",
    #         description=(
    #             "How to order the search results, only when the user asks for an order. "
    #             "One of: 'price_low_to_high' (cheapest first), 'price_high_to_low' (most "
    #             "expensive first), 'average_review' (best rated), 'newest_arrivals' (newest), "
    #             "'bestsellers' (best selling), 'featured' (default)."
    #         ),
    #     ),
    ParameterConfig(
        code="query",
        name="Query",
        type="string",
        description=(
            "The question to search documents for, written to stand alone: include what "
            "earlier messages refer to ('return window for opened headphones', not 'what "
            "about returning it?')."
        ),
    ),
]
