from .search_products import SEARCH_PRODUCTS

# All available tools
TOOLS = [SEARCH_PRODUCTS]

# Lookup tools by code
TOOLS_BY_CODE = {tool.code: tool for tool in TOOLS}
