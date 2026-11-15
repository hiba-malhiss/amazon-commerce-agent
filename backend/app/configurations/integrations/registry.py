from app.configurations.schemas import APIIntegrationConfig, RAGIntegrationConfig
from app.configurations.tools.registry import TOOLS_BY_CODE

from .amazon_product_details import AMAZON_PRODUCT_DETAILS
from .amazon_product_search import AMAZON_PRODUCT_SEARCH
from .policies_rag import POLICIES_RAG

# Registered integrations
INTEGRATIONS = [AMAZON_PRODUCT_SEARCH, AMAZON_PRODUCT_DETAILS, POLICIES_RAG]

# Lookup integrations by code
INTEGRATIONS_BY_CODE = {integration.code: integration for integration in INTEGRATIONS}


def tool_integration(tool_code: str) -> APIIntegrationConfig | RAGIntegrationConfig | None:
    """The integration a tool runs through, or None when it has none."""
    tool = TOOLS_BY_CODE.get(tool_code)
    if tool is None or tool.integration_code is None:
        return None
    return INTEGRATIONS_BY_CODE.get(tool.integration_code)
