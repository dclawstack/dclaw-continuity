import hashlib
import math
import os
import struct

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.main import app
from app.core.config import settings
from app.core.database import get_db
from app.models.base import Base
from app.services import embedding as embedding_module
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
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
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
    # Service modules imported get_llm_client at module load time, so patch the
    # bound names too.
    from app.services import (
        bcp_service,
        communication_service,
        copilot_service,
        exercise_service,
        impact_service,
        it_dr_service,
        recovery_service,
        regulatory_service,
        supply_chain_service,
        vendor_service,
        work_area_service,
    )

    for mod in (
        bcp_service,
        communication_service,
        copilot_service,
        exercise_service,
        impact_service,
        it_dr_service,
        recovery_service,
        regulatory_service,
        supply_chain_service,
        vendor_service,
        work_area_service,
    ):
        monkeypatch.setattr(mod, "get_llm_client", lambda: fake)
    return fake


def _deterministic_embedding(text: str, dim: int) -> list[float]:
    """Deterministic float vector seeded by SHA256(text). Unit-normalized."""
    h = hashlib.sha256(text.encode("utf-8")).digest()
    # Repeat the hash to fill `dim` floats (8 bytes per float).
    needed = dim * 8
    buf = (h * ((needed // len(h)) + 1))[:needed]
    raw = [struct.unpack(">d", buf[i * 8 : (i + 1) * 8])[0] for i in range(dim)]
    # Map to [-1, 1] roughly + L2 normalize.
    cleaned = [(v % 2.0) - 1.0 for v in raw]
    norm = math.sqrt(sum(x * x for x in cleaned)) or 1.0
    return [x / norm for x in cleaned]


class FakeEmbedding:
    """Deterministic in-process embedder."""

    def __init__(self, dim: int):
        self.dim = dim
        self.calls = 0

    async def embed(self, text: str) -> list[float]:
        self.calls += 1
        return _deterministic_embedding(text, self.dim)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        self.calls += len(texts)
        return [_deterministic_embedding(t, self.dim) for t in texts]


@pytest.fixture(autouse=True)
def fake_embedder(monkeypatch):
    """Autouse: no test should hit the real Ollama embed endpoint."""

    fake = FakeEmbedding(settings.embedding_dim)
    monkeypatch.setattr(embedding_module, "get_embedding_client", lambda: fake)
    from app.services import rag_service

    monkeypatch.setattr(rag_service, "get_embedding_client", lambda: fake)
    return fake
