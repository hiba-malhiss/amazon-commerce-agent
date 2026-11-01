from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agent.graph import build_graph
from app.conversations.routes import router as threads_router
from app.database.checkpointer import postgres_checkpointer


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    return {"status": "ok"}

app.include_router(threads_router)