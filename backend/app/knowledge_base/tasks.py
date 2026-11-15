"""Celery tasks of the knowledge base: thin wrappers that run the async service code."""

import asyncio
from pathlib import Path
from uuid import UUID

from app.core.settings import settings
from app.knowledge_base.services.indexing import RETRYABLE_ERRORS, index_uploaded_document
from app.knowledge_base.services.knowledge_base import INDEX_DOCUMENT_TASK
from app.worker.celery_app import celery_app


@celery_app.task(
    bind=True,
    name=INDEX_DOCUMENT_TASK,
    # Retry on these errors
    autoretry_for=RETRYABLE_ERRORS,
    max_retries=settings.indexing_max_retries,
    # Wait up to 30s before the first retry, then up to 60s, 120s ... (max 600s): a rate
    # limit needs time to pass
    retry_backoff=30,
    retry_backoff_max=600,
    # Pick each wait at random below that limit, so failed jobs don't all retry at once
    retry_jitter=True,
)
def index_document(self, document_id: str, path: str, kb_code: str) -> None:
    final_attempt = self.request.retries >= self.max_retries
    asyncio.run(
        index_uploaded_document(UUID(document_id), Path(path), kb_code, final_attempt=final_attempt)
    )
