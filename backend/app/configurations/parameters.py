from app.configurations.schemas import ParameterConfig

PARAMETERS = [
    ParameterConfig(
        code="query",
        name="Search Query",
        type="string",
        description="Product search query",
    ),
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
        description="Product category",
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
]
