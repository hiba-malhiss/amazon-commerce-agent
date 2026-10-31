
import pytest

from app.agent.entity_mapper import map_entities
from app.config.integrations.amazon_product_search import AMAZON_PRODUCT_SEARCH
from app.integrations.api_executor import execute_api


@pytest.mark.anyio
async def test_amazon_product_search():
    # Simulate extracted global parameters
    parameters = {
        "query": "Samsung headphones",
    }

    # Execute the API integration
    response = await execute_api(
        AMAZON_PRODUCT_SEARCH,
        parameters,
    )

    # Map API response into entities
    mapping = AMAZON_PRODUCT_SEARCH.entity_mapping
    assert mapping is not None

    entities = map_entities(response, mapping)

    assert len(entities) > 0

    # Display first three entities
    for entity in entities[:3]:
        print(entity)


@pytest.fixture
def anyio_backend():
    return "asyncio"
