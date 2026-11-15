from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.schemas.resolution import RetrievedChunks
from app.configurations.knowledge_bases.registry import KNOWLEDGE_BASES_BY_CODE
from app.configurations.schemas import RAGIntegrationConfig
from app.knowledge_base.processing.embedding import embed_query
from app.knowledge_base.repositories import KnowledgeChunkRepository


async def search_chunks(
    session: AsyncSession, integration: RAGIntegrationConfig, query: str
) -> list[RetrievedChunks]:
    """The chunks closest to the query in the integration's knowledge base, best first.

    Only `ready` documents are searched. The `top_k` closest chunks come back with their
    score (cosine similarity, 0 to 1), unfiltered: the caller applies the relevance
    threshold, so traces and evaluations can still see the chunks it rejects.
    """
    config = KNOWLEDGE_BASES_BY_CODE[integration.knowledge_base_code]
    rows = await KnowledgeChunkRepository(session).search(
        config.code, await embed_query(query, config), integration.top_k
    )

    chunks: list[RetrievedChunks] = [
        {
            "chunk_id": chunk.id,
            "content": chunk.content,
            "document_id": str(chunk.document_id),
            "filename": filename,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
            "section_title": chunk.section_path,
            "score": round(1 - row_distance, 4),
        }
        for chunk, filename, row_distance in rows
    ]

    return chunks
