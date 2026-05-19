import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.main import app
from app.core.config import settings
from app.core.database import get_db
from app.models.base import Base
from app.services import llm as llm_module

TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_continuity_test",
)

test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)


async def override_get_db():
    async with AsyncSession(test_engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def authed_client(client):
    client.headers["Authorization"] = f"Bearer {settings.dev_auth_token}"
    yield client


class FakeLLM:
    """Captures requests and returns canned responses."""

    def __init__(self):
        self.calls: list[dict] = []
        self.json_response: dict = {}
        self.text_response: str = "ok"

    async def chat(self, messages, *, json_mode: bool = False, temperature: float = 0.2):
        self.calls.append({"messages": list(messages), "json_mode": json_mode})
        return self.text_response

    async def chat_json(self, messages, *, temperature: float = 0.2):
        self.calls.append({"messages": list(messages), "json_mode": True})
        return self.json_response


@pytest.fixture
def fake_llm(monkeypatch):
    fake = FakeLLM()
    monkeypatch.setattr(llm_module, "get_llm_client", lambda: fake)
    # Service modules import get_llm_client at module load time; patch the
    # bound name in each one so they pick up the fake.
    from app.services import (
        bcp_service,
        copilot_service,
        impact_service,
        recovery_service,
    )

    for mod in (bcp_service, copilot_service, impact_service, recovery_service):
        monkeypatch.setattr(mod, "get_llm_client", lambda: fake)
    return fake
