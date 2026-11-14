from .amazon_product_details import AMAZON_PRODUCT_DETAILS
from .amazon_product_search import AMAZON_PRODUCT_SEARCH
from .policies_rag import POLICIES_RAG

# Registered integrations
INTEGRATIONS = [AMAZON_PRODUCT_SEARCH, AMAZON_PRODUCT_DETAILS, POLICIES_RAG]

# Lookup integrations by code
INTEGRATIONS_BY_CODE = {integration.code: integration for integration in INTEGRATIONS}
