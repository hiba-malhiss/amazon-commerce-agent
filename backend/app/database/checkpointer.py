import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

load_dotenv()

# Setup/open resources => yield (give it to caller) => clean up
@asynccontextmanager
async def postgres_checkpointer():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is not configured")

    async with AsyncPostgresSaver.from_conn_string(database_url) as saver:
        await saver.setup() # Creates or prepares checkpoint tables.
        yield saver
