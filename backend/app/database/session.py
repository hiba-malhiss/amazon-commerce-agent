import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

database_url = os.getenv("SQLALCHEMY_DATABASE_URL")

if not database_url:
    raise ValueError("SQLALCHEMY_DATABASE_URL is not configured")

# Shared asynchronous PostgreSQL engine
engine = create_async_engine(database_url, pool_pre_ping=True)

# Factory for database sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    # Provide one database session per request
    async with AsyncSessionLocal() as session:
        yield session
