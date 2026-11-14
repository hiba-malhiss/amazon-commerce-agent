from app.knowledge_base.config import KnowledgeBaseConfig

STORE_POLICIES = KnowledgeBaseConfig(
    code="store_policies",
    name="Store Policies",
)

KNOWLEDGE_BASES = [STORE_POLICIES]

KNOWLEDGE_BASES_BY_CODE = {kb.code: kb for kb in KNOWLEDGE_BASES}
