import time

from langgraph.config import get_stream_writer

from app.agent.state import ToolRequestState, ToolRequestUpdate
from app.agent.utils.timing import elapsed_ms
from app.configurations.integrations.registry import tool_integration
from app.configurations.schemas import RAGIntegrationConfig
from app.database.session import AsyncSessionLocal
from app.knowledge_base.services.retrieval import search_chunks


async def rag_search_node(state: ToolRequestState) -> ToolRequestUpdate:
    """Search the knowledge base of the tool's RAG integration for the request's query."""
    writer = get_stream_writer()
    request = state["request"]

    integration = tool_integration(request["tool"])
    if not isinstance(integration, RAGIntegrationConfig):
        return failed(state, "Unknown or unsupported integration")

    query = str(request["parameters"][integration.query_parameter])
    writer(
        {
            "node": "rag_search",
            "status": "started",
            "data": {
                "request_id": state["id"],
                "integration": integration.code,
                "knowledge_base": integration.knowledge_base_code,
                "query": query,
            },
        }
    )

    started = time.perf_counter()
    try:
        async with AsyncSessionLocal() as session:
            chunks = await search_chunks(session, integration, query)
    except Exception as error:
        return failed(state, str(error), elapsed_ms(started))

    # Only chunks at or above the threshold reach the reply; the trace shows them all
    threshold = integration.relevance_threshold
    relevant = [c for c in chunks if threshold is None or c["score"] >= threshold]

    writer(
        {
            "node": "rag_search",
            "status": "completed",
            "data": {
                "request_id": state["id"],
                "duration_ms": elapsed_ms(started),
                "relevance_threshold": threshold,
                "chunks": [
                    {
                        "filename": chunk["filename"],
                        "section": chunk["section_title"],
                        "score": chunk["score"],
                    }
                    for chunk in chunks
                ],
            },
        }
    )
    return {
        "outcome": {
            "id": state["id"],
            "status": "success" if relevant else "no_relevant_results",
            "result": {"type": "chunks", "chunks": relevant},
            "missing_parameters": [],
            "error": None,
        }
    }


def failed(
    state: ToolRequestState, error: str, duration_ms: int | None = None
) -> ToolRequestUpdate:
    get_stream_writer()(
        {
            "node": "rag_search",
            "status": "failed",
            "data": {"request_id": state["id"], "error": error, "duration_ms": duration_ms},
        }
    )
    return {
        "outcome": {
            "id": state["id"],
            "status": "fail",
            "result": None,
            "missing_parameters": [],
            "error": "Unable to search the documents",
        }
    }
