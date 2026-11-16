"""The Celery app: background jobs run by a separate worker process.

Start it from backend/:  uv run celery -A app.worker.celery_app worker --loglevel=info
"""

from celery import Celery

from app.core.settings import settings

celery_app = Celery(
    "amazon_commerce_agent",
    broker=settings.redis_url,
    include=["app.knowledge_base.tasks"],  # task path
)

# celery_app receives background jobs, puts them in a queue, and makes sure workers run them.
# The broker (Redis) holds the messages (jobs) until a worker picks them up.
# Idempotent: running the same task multiple times must not create duplicate or corrupted
# results.
celery_app.conf.update(
    task_serializer="json",  # use JSON when sending tasks.
    accept_content=["json"],  # workers accept JSON messages.
    # Ack a job only after it's done; if the worker crashes it's rejected instead. No ack means
    # the broker keeps the job and it's processed again
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Worker reserve one job at a time
    worker_prefetch_multiplier=1,
    # Progress is saved on the document row, so no result backend is needed
    task_ignore_result=True,
    broker_connection_retry_on_startup=True,
)
