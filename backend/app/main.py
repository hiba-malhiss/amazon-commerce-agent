import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agent.graph import build_graph
from app.configurations.validator import validate_config
from app.conversations.routes import router as conversations_router
from app.conversations.websocket import router as websocket_router
from app.database.checkpointer import postgres_checkpointer
from app.knowledge_base.routes import router as knowledge_base_router
from app.worker.celery_app import indexing_worker_online


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail at startup, not mid-conversation, when tools, parameters, integrations,
    # entities, or knowledge bases don't fit together
    validate_config()

    async with postgres_checkpointer() as checkpointer:
        app.state.agent_graph = build_graph(checkpointer)
        yield


# Before yield → Runs once when the app starts.
# After yield → Runs when the app shuts down.
app = FastAPI(
    title="Amazon Commerce Agent",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    # "down" means uploads will sit on `indexing`: start the worker (see scripts/dev.sh)
    worker_online = await asyncio.to_thread(indexing_worker_online)
    return {"status": "ok", "indexing_worker": "up" if worker_online else "down"}


app.include_router(conversations_router)
app.include_router(websocket_router)
app.include_router(knowledge_base_router)
