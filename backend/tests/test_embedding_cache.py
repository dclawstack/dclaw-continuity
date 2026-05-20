"""Verify the EmbeddingClient consults Redis before hitting Ollama."""

from __future__ import annotations

import pytest
import pytest_asyncio
from fakeredis import aioredis as fake_aioredis

from app.services.embedding import EmbeddingClient


@pytest_asyncio.fixture
async def fake_redis():
    """A fresh in-memory Redis per test."""
    client = fake_aioredis.FakeRedis(decode_responses=False)
    yield client
    await client.aclose()


class FakeHTTPCounter:
    """Stand-in for the Ollama HTTP path. Counts calls + returns canned vectors."""

    def __init__(self):
        self.calls = 0

    async def fetch(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        # one deterministic 4-dim vec per input
        return [[float(i), 0.0, 0.0, 1.0] for i, _ in enumerate(texts)]


@pytest.mark.asyncio
async def test_cache_hit_skips_ollama(fake_redis, monkeypatch):
    counter = FakeHTTPCounter()
    client = EmbeddingClient(cache=fake_redis)
    monkeypatch.setattr(client, "_fetch_from_ollama", counter.fetch)

    # First call → miss → Ollama hit
    a = await client.embed("hello world")
    assert counter.calls == 1

    # Second call with same text → cache hit → no Ollama call
    b = await client.embed("hello world")
    assert counter.calls == 1
    assert a == b


@pytest.mark.asyncio
async def test_partial_cache_hit(fake_redis, monkeypatch):
    counter = FakeHTTPCounter()
    client = EmbeddingClient(cache=fake_redis)
    monkeypatch.setattr(client, "_fetch_from_ollama", counter.fetch)

    await client.embed("alpha")  # populates cache
    assert counter.calls == 1

    # Mixed batch: one cached, one fresh — Ollama only sees the fresh one
    results = await client.embed_batch(["alpha", "beta"])
    assert len(results) == 2
    assert counter.calls == 2
    # Subsequent batch with both cached → no new Ollama call
    await client.embed_batch(["alpha", "beta"])
    assert counter.calls == 2


@pytest.mark.asyncio
async def test_no_cache_when_disabled(monkeypatch):
    """Passing cache=None disables the cache; every call hits Ollama."""
    counter = FakeHTTPCounter()
    client = EmbeddingClient(cache=None)
    monkeypatch.setattr(client, "_fetch_from_ollama", counter.fetch)

    await client.embed("hello")
    await client.embed("hello")
    assert counter.calls == 2
