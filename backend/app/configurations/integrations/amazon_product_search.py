from app.configurations.schemas import (
    APIIntegrationConfig,
    AuthenticationConfig,
    EntityMappingConfig,
)

AMAZON_PRODUCT_SEARCH = APIIntegrationConfig(
    code="amazon_product_search",
    name="Amazon Product Search",
    description="Search Amazon products using SearchAPI.io",
    url="https://www.searchapi.io/api/v1/search",
    method="GET",
    static_query_params={
        "engine": "amazon_search",
    },
    query_params={
        "q": "query",
        "currency": "currency",
        "price_min": "min_price",
        "price_max": "max_price",
    },
    entity_mapping=EntityMappingConfig(
        entity_code="product",
        collection_path="organic_results",
        field_mapping={
            "product_id": "asin",
            "product_name": "title",
            "brand": "brand",
            "price": "extracted_price",
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
