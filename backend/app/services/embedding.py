"""Text embeddings via Ollama (best-effort) with optional Redis cache.

Ollama's `/api/embed` endpoint accepts a model + input (str or list[str]) and
returns `{"embeddings": [[...], ...]}`. If Ollama is not running, callers
should treat embedding as unavailable — indexing & retrieval become no-ops.

If Redis is reachable, we look up cached vectors before calling Ollama (keyed
by sha256(model + text)) and write fresh results back. Cache misses still
hit Ollama, cache hits skip the network call entirely. Any Redis error is
swallowed — we never block the user on cache problems.
"""

from __future__ import annotations

import hashlib
import struct

import httpx
from redis import asyncio as aioredis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.logging import get_logger
from app.core.redis import get_redis

log = get_logger(__name__)


class EmbeddingUnavailable(RuntimeError):
    pass


def _cache_key(model: str, text: str) -> str:
    h = hashlib.sha256(f"{model}\x00{text}".encode()).hexdigest()
    return f"emb:{h}"


def _vec_to_bytes(vec: list[float]) -> bytes:
    return struct.pack(f"<{len(vec)}f", *vec)


def _bytes_to_vec(b: bytes) -> list[float]:
    n = len(b) // 4
    return list(struct.unpack(f"<{n}f", b))


class EmbeddingClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
        cache: aioredis.Redis | None = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_embed_model
        self.timeout = timeout or settings.llm_request_timeout
        # Caller can pass `cache=None` to disable; default reads global config.
        self.cache = cache if cache is not None else get_redis()
        self.cache_ttl = settings.redis_embed_cache_ttl_seconds

    async def embed(self, text: str) -> list[float]:
        result = await self.embed_batch([text])
        if not result:
            raise EmbeddingUnavailable("empty response")
        return result[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        # Fast path: try Redis for every text; remember the misses.
        cached: dict[int, list[float]] = {}
        misses: list[tuple[int, str]] = []
        if self.cache is not None:
            try:
                keys = [_cache_key(self.model, t) for t in texts]
                blobs = await self.cache.mget(keys)
                for i, blob in enumerate(blobs):
                    if blob is None:
                        misses.append((i, texts[i]))
                    else:
                        cached[i] = _bytes_to_vec(blob)
            except RedisError as exc:
                log.warning("redis_mget_failed", error=str(exc))
                misses = list(enumerate(texts))
        else:
            misses = list(enumerate(texts))

        # Slow path: fetch the misses from Ollama.
        fetched: list[list[float]] = []
        if misses:
            fetched = await self._fetch_from_ollama([t for _, t in misses])
            if len(fetched) != len(misses):
                raise EmbeddingUnavailable(
                    f"ollama returned {len(fetched)} embeddings for {len(misses)} inputs"
                )

            # Write the fetched vectors back to Redis (best-effort).
            if self.cache is not None:
                try:
                    async with self.cache.pipeline(transaction=False) as pipe:
                        for (_, text), vec in zip(misses, fetched, strict=True):
                            pipe.set(
                                _cache_key(self.model, text),
                                _vec_to_bytes(vec),
                                ex=self.cache_ttl,
                            )
                        await pipe.execute()
                except RedisError as exc:
                    log.warning("redis_setex_failed", error=str(exc))

        # Stitch cached + fetched back in original order.
        result: list[list[float]] = [None] * len(texts)  # type: ignore[list-item]
        for i, vec in cached.items():
            result[i] = vec
        for (idx, _), vec in zip(misses, fetched, strict=True):
            result[idx] = vec
        return result

    async def _fetch_from_ollama(self, texts: list[str]) -> list[list[float]]:
        url = f"{self.base_url}/api/embed"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json={"model": self.model, "input": texts})
                if resp.status_code >= 400:
                    raise EmbeddingUnavailable(
                        f"ollama embed {resp.status_code}: {resp.text[:200]}"
                    )
                data = resp.json()
        except httpx.RequestError as exc:
            raise EmbeddingUnavailable(f"ollama unreachable: {exc}") from exc

        # Newer Ollama returns "embeddings"; some versions return "embedding".
        emb = data.get("embeddings") or ([data["embedding"]] if "embedding" in data else None)
        if not emb:
            raise EmbeddingUnavailable(f"unexpected response: {data}")
        return emb


_singleton: EmbeddingClient | None = None


def get_embedding_client() -> EmbeddingClient:
    global _singleton
    if _singleton is None:
        _singleton = EmbeddingClient()
    return _singleton
