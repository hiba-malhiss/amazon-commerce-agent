from haystack import Document
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.utils import Secret

from app.core.settings import settings
from app.knowledge_base.config import KnowledgeBaseConfig
from app.knowledge_base.models import EMBEDDING_DIMENSIONS

# Chunks per embedding API call
BATCH_SIZE = 64


async def embed_chunks(chunks: list[Document], config: KnowledgeBaseConfig) -> list[Document]:
    """The chunks with their embedding set, one API call per batch. Fails on any error,
    so a document is never stored with some chunks missing their vector."""

    if not chunks:
        return []

    embedder = OpenAIDocumentEmbedder(
        api_key=openai_key(),
        model=config.embedding_model,
        dimensions=EMBEDDING_DIMENSIONS,
        batch_size=BATCH_SIZE,
        progress_bar=False,
        raise_on_failure=True,
    )
    documents = (await embedder.run_async(documents=chunks))["documents"]

    if any(len(document.embedding or []) != EMBEDDING_DIMENSIONS for document in documents):
        raise ValueError(f"Expected {EMBEDDING_DIMENSIONS}-dimension embeddings for every chunk")
    return documents


async def embed_query(text: str, config: KnowledgeBaseConfig) -> list[float]:
    """The embedding of a search query, with the same model as the knowledge base's chunks."""

    embedder = OpenAITextEmbedder(
        api_key=openai_key(), model=config.embedding_model, dimensions=EMBEDDING_DIMENSIONS
    )
    return (await embedder.run_async(text=text))["embedding"]


def openai_key() -> Secret:
    return Secret.from_token(settings.openai_api_key.get_secret_value())
