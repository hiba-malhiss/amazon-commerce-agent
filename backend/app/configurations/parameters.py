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
        code="features",
        name="Features",
        type="list",
        description="Key feature bullet points of a product",
    ),
]
