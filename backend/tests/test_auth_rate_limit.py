"""Brute-force protection on the auth endpoints.

The limiter is best-effort and Redis-backed; conftest empties redis_url so the
rest of the suite no-ops it. Here we monkeypatch the module's get_redis to an
in-memory fakeredis so the real HTTP wiring is exercised end-to-end.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from fakeredis import aioredis as fake_aioredis

from app.core import rate_limit
from app.core.config import settings


@pytest_asyncio.fixture
async def fake_redis(monkeypatch):
    client = fake_aioredis.FakeRedis(decode_responses=False)
    monkeypatch.setattr(rate_limit, "get_redis", lambda: client)
    yield client
    await client.aclose()


@pytest.mark.asyncio
async def test_login_ip_rate_limited(client, fake_redis):
    """The (per_minute + 1)th request from one IP gets 429, not 401."""
    creds = {"email": "nobody@example.com", "password": "wrong-pw-12345"}

    for _ in range(settings.auth_rate_limit_per_minute):
        resp = await client.post("/api/v1/auth/login", json=creds)
        assert resp.status_code == 401, resp.text

    resp = await client.post("/api/v1/auth/login", json=creds)
    assert resp.status_code == 429, resp.text
    assert "slow down" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_account_locks_after_failed_logins(client, fake_redis, monkeypatch):
    """A real account locks (429) after N bad passwords, even with the right one."""
    # Take the per-IP limit out of the way so we isolate the account lockout.
    monkeypatch.setattr(settings, "auth_rate_limit_per_minute", 1000)

    email = "victim@example.com"
    good = "correct-horse-123"
    signup = await client.post("/api/v1/auth/signup", json={"email": email, "password": good})
    assert signup.status_code == 201, signup.text

    for _ in range(settings.auth_max_failed_logins):
        resp = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": "bad-password"}
        )
        assert resp.status_code == 401, resp.text

    # Now even the correct password is refused with a lockout 429.
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": good})
    assert resp.status_code == 429, resp.text
    assert "locked" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_successful_login_clears_failure_counter(client, fake_redis, monkeypatch):
    """A success below the threshold resets the counter, so it can't accrete."""
    monkeypatch.setattr(settings, "auth_rate_limit_per_minute", 1000)

    email = "comeback@example.com"
    good = "correct-horse-123"
    await client.post("/api/v1/auth/signup", json={"email": email, "password": good})

    # A few failures, then a success — counter should be wiped.
    for _ in range(settings.auth_max_failed_logins - 1):
        await client.post("/api/v1/auth/login", json={"email": email, "password": "nope-12345"})
    ok = await client.post("/api/v1/auth/login", json={"email": email, "password": good})
    assert ok.status_code == 200, ok.text
    assert await fake_redis.get(f"rl:auth:fail:{email}") is None

    # The full threshold of failures is once again required to lock out.
    for _ in range(settings.auth_max_failed_logins):
        resp = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": "nope-12345"}
        )
        assert resp.status_code == 401, resp.text
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": good})
    assert resp.status_code == 429, resp.text
