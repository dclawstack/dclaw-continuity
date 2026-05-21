from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.models.base import Base

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "dev",
    pool_pre_ping=True,
)


async def get_db() -> AsyncSession:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Bring the schema online on a fresh database.

    The pgvector extension has to be installed before `create_all` because
    the `knowledge_chunks` table uses a `vector(768)` column. Production
    deploys should run `alembic upgrade head` instead, which handles this
    via migration 0004; this path is for first-boot convenience in
    docker-compose / dev.
    """
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
