from pydantic import BaseModel


class KnowledgeBaseSummary(BaseModel):
    code: str
    name: str
