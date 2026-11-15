from .store_policies import STORE_POLICIES

# Registered knowledge bases
KNOWLEDGE_BASES = [STORE_POLICIES]

# Lookup knowledge bases by code
KNOWLEDGE_BASES_BY_CODE = {kb.code: kb for kb in KNOWLEDGE_BASES}
