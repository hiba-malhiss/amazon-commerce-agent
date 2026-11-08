from app.configurations.schemas import (
    APIIntegrationConfig,
    AuthenticationConfig,
    EntityMappingConfig,
)

# SearchAPI.io has no comparison endpoint: a comparison fetches each product's details
# (one request per product, run in parallel) and the reply compares them
AMAZON_PRODUCT_DETAILS = APIIntegrationConfig(
    code="amazon_product_details",
    name="Amazon Product Details",
    description="Get one Amazon product's details by ASIN using SearchAPI.io",
    url="https://www.searchapi.io/api/v1/search",
    method="GET",
    static_query_params={
        "engine": "amazon_product",
    },
    query_params={
        "asin": "product_id",
        "currency": "currency",
    },
    entity_mapping=EntityMappingConfig(
        entity_code="product",
        collection_path="product",  # one object, not a list
        field_mapping={
            "product_id": "asin",
            "product_name": "title",
            "price": "buybox.price.value",
            "rating": "rating",
            "review_count": "reviews",
            "features": "feature_bullets",
        },
    ),
    authentication=AuthenticationConfig(
        type="api_key",
        key_name="Authorization",
        key_location="header",
        key_prefix="Bearer ",
        api_key_env="SEARCHAPI_API_KEY",
    ),
)
