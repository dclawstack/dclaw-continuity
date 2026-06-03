"""Best-effort brute-force protection for auth endpoints.

Two Redis-backed layers, both fixed-window:
  1. Per-IP request rate limit on auth endpoints (signup + login).
  2. Per-account lockout after repeated failed logins.

Best-effort like the rest of the app (see app.core.redis): if Redis is empty
or unreachable, we log and allow the request rather than locking everyone out
of a degraded system.
"""

from __future__ import annotations

from fastapi import HTTPException, Request, status
from redis import asyncio as aioredis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.logging import get_logger
from app.core.redis import get_redis

log = get_logger(__name__)


def _client_ip(request: Request) -> str:
    # Honour the first X-Forwarded-For hop when behind a proxy/ingress, else the
    # direct peer. Falls back to a constant so a missing client still buckets.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _hit(redis: aioredis.Redis, key: str, ttl: int) -> int:
    """INCR `key`, setting its TTL on the first hit. Returns the new count."""
    count = int(await redis.incr(key))
    if count == 1:
        await redis.expire(key, ttl)
    return count


async def enforce_ip_rate_limit(request: Request) -> None:
    """FastAPI dependency: 429 once an IP exceeds the per-minute auth budget."""
    redis = get_redis()
    if redis is None:
        return
    ip = _client_ip(request)
    try:
        count = await _hit(redis, f"rl:auth:ip:{ip}", 60)
    except RedisError as exc:
        log.warning("rate_limit_redis_failed", error=str(exc))
        return
    if count > settings.auth_rate_limit_per_minute:
        log.warning("auth_ip_rate_limited", ip=ip, count=count)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="too many requests; please slow down",
        )


async def check_account_lock(email: str) -> None:
    """Raise 429 if this account has too many recent failed logins."""
    redis = get_redis()
    if redis is None:
        return
    try:
        raw = await redis.get(f"rl:auth:fail:{email.lower()}")
    except RedisError as exc:
        log.warning("rate_limit_redis_failed", error=str(exc))
        return
    if raw is not None and int(raw) >= settings.auth_max_failed_logins:
        log.warning("auth_account_locked", email=email.lower())
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="too many failed attempts; account temporarily locked",
        )


async def record_failed_login(email: str) -> None:
    """Count one failed login, expiring after the lockout window."""
    redis = get_redis()
    if redis is None:
        return
    try:
        await _hit(redis, f"rl:auth:fail:{email.lower()}", settings.auth_lockout_window_seconds)
    except RedisError as exc:
        log.warning("rate_limit_redis_failed", error=str(exc))


async def clear_failed_logins(email: str) -> None:
    """Reset the failure counter after a successful login."""
    redis = get_redis()
    if redis is None:
        return
    try:
        await redis.delete(f"rl:auth:fail:{email.lower()}")
    except RedisError as exc:
        log.warning("rate_limit_redis_failed", error=str(exc))
