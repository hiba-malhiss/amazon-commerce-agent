"""Live document updates. The API and the Celery worker (another process) publish each
document change to Redis; the knowledge base WebSocket forwards them to the page."""

import logging
from collections.abc import AsyncIterator

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.settings import settings
from app.knowledge_base.models import KnowledgeDocument
from app.knowledge_base.schemas import DocumentEvent, IndexingStep, KnowledgeDocumentResponse

logger = logging.getLogger(__name__)


def channel(kb_code: str) -> str:
    return f"knowledge_documents:{kb_code}"


async def publish_document_event(
    document: KnowledgeDocument, *, step: IndexingStep | None = None, deleted: bool = False
) -> None:
    """Best effort: a lost update must not fail the upload or the indexing (the page reloads
    the list whenever its connection opens)."""
    event = DocumentEvent(
        type="deleted" if deleted else "updated",
        document=KnowledgeDocumentResponse.model_validate(document),
        step=step,
    )
    try:
        async with Redis.from_url(settings.redis_url) as client:
            # Redis Pub/Sub transport strings only => model_dump_json stringify json
            await client.publish(channel(document.knowledge_base_code), event.model_dump_json())
    except RedisError:
        logger.warning("Couldn't publish an update for document %s", document.id, exc_info=True)


async def listen_document_events(kb_code: str) -> AsyncIterator[str]:
    """The knowledge base's document events (JSON), as they're published."""
    async with Redis.from_url(settings.redis_url) as client, client.pubsub() as pubsub:
        await pubsub.subscribe(channel(kb_code))
        async for message in pubsub.listen():
            if message["type"] == "message":
                # Redis turn str to bytes => decode converts bytes into a string
                yield message["data"].decode()
