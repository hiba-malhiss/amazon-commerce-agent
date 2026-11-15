from .product_details import PRODUCT_DETAILS
from .search_policies import SEARCH_POLICIES
from .search_products import SEARCH_PRODUCTS

# All available tools
TOOLS = [SEARCH_PRODUCTS, PRODUCT_DETAILS, SEARCH_POLICIES]

# Lookup tools by code
TOOLS_BY_CODE = {tool.code: tool for tool in TOOLS}
