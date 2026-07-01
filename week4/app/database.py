from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from week4.app.config import DATABASE_URL

# connection manager
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# creates session
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session
