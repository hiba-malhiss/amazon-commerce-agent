from app.configurations.schemas import ToolConfig

SEARCH_POLICIES = ToolConfig(
    code="search_policies",
    name="Search Store Policies",
    description=(
        "Answer questions about the store's policies: returns and refunds, shipping and "
        "delivery, warranty and protection plans, payment methods and billing."
    ),
    required_parameters=["query"],
    integration_code="policies_rag",
)
