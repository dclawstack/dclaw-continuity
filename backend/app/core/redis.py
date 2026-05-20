"""Async Redis client.

Used for the embedding cache today; will host rate-limits / queues later.
Best-effort: if `REDIS_URL` is empty or the server is unreachable, callers
should treat Redis as unavailable — never let it block a user request.
"""

from __future__ import annotations

from typing import Optional

from redis import asyncio as aioredis

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


_client: Optional[aioredis.Redis] = None


def get_redis() -> Optional[aioredis.Redis]:
    """Return a shared async Redis client, or None if disabled.

    Connection errors don't raise here — they surface only on the first
    actual command, where the caller is expected to catch
    `redis.exceptions.RedisError` (and its subclasses) and degrade.
    """
    global _client
    if not settings.redis_url:
        return None
    if _client is None:
        _client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=False,  # we store raw bytes for embedding vectors
        )
    return _client


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
