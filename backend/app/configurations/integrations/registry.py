from .amazon_product_details import AMAZON_PRODUCT_DETAILS
from .amazon_product_search import AMAZON_PRODUCT_SEARCH

# Registered integrations
INTEGRATIONS = [
    AMAZON_PRODUCT_SEARCH,
    AMAZON_PRODUCT_DETAILS,
]

# Lookup integrations by code
INTEGRATIONS_BY_CODE = {integration.code: integration for integration in INTEGRATIONS}
