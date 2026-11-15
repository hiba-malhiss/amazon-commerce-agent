from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.schemas.resolution import RetrievedChunks
from app.configurations.schemas import RAGIntegrationConfig
from app.knowledge_base.embedding import embed_query
from app.knowledge_base.models import KnowledgeChunk, KnowledgeDocument
from app.knowledge_base.registry import KNOWLEDGE_BASES_BY_CODE


async def search_chunks(
    session: AsyncSession, integration: RAGIntegrationConfig, query: str
) -> list[RetrievedChunks]:
    """The chunks closest to the query in the integration's knowledge base, best first.

    Only `ready` documents are searched. The `top_k` closest chunks come back with their
    score (cosine similarity, 0 to 1), unfiltered: the caller applies the relevance
    threshold, so traces and evaluations can still see the chunks it rejects.
    """
    config = KNOWLEDGE_BASES_BY_CODE[integration.knowledge_base_code]
    # creates a SQL expression that: calculates the cosine distance between
    # The users query embedding AND each stored chunk embedding.
    distance = KnowledgeChunk.embedding.cosine_distance(await embed_query(query, config))

    rows = await session.execute(
        select(KnowledgeChunk, KnowledgeDocument.filename, distance.label("distance"))
        .join(KnowledgeDocument)
        .where(
            KnowledgeChunk.knowledge_base_code == config.code,
            KnowledgeDocument.status == "ready",
        )
        .order_by(distance)
        .limit(integration.top_k)
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
