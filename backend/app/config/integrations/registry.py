from .amazon_product_search import AMAZON_PRODUCT_SEARCH

# Registered integrations
INTEGRATIONS = [
    AMAZON_PRODUCT_SEARCH,
]

# Lookup integrations by code
INTEGRATIONS_BY_CODE = {integration.code: integration for integration in INTEGRATIONS}
