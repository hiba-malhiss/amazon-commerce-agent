import pytest

from app.agent.tool_graph import build_tool_graph


@pytest.mark.anyio
async def test_amazon_product_search():
    # Calls the real SearchAPI through the tool workflow (needs SEARCHAPI_API_KEY)
    final = await build_tool_graph().ainvoke(
        {
            "id": "live-test",
            "request": {
                "question": "Samsung headphones",
                "tool": "search_products",
                "entities": [],
                "parameters": {"query": "Samsung headphones"},
                "relation": "new",
                "source_request_id": None,
            },
        }
    )

    outcome = final["outcome"]
    assert outcome["status"] == "success", outcome["error"]
    entities = outcome["result"]["entities"]
    assert len(entities) > 0

    # Display first three entities
    for entity in entities[:3]:
        print(entity)


@pytest.fixture
def anyio_backend():
    return "asyncio"
