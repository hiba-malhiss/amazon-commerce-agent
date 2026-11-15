from app.configurations.schemas import RAGIntegrationConfig

POLICIES_RAG = RAGIntegrationConfig(
    code="policies_rag",
    name="Store Policies RAG",
    description="Search store policy documents",
    knowledge_base_code="store_policies",
    top_k=5,
    relevance_threshold=0.3,
)
