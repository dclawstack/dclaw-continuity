"""Text embeddings via Ollama (best-effort).

Ollama's `/api/embed` endpoint accepts a model + input (str or list[str]) and
returns `{"embeddings": [[...], ...]}`. If Ollama is not running, callers
should treat embedding as unavailable — indexing & retrieval become no-ops.
"""

from __future__ import annotations

from typing import Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


class EmbeddingUnavailable(RuntimeError):
    pass


class EmbeddingClient:
    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_embed_model
        self.timeout = timeout or settings.llm_request_timeout

    async def embed(self, text: str) -> list[float]:
        result = await self.embed_batch([text])
        if not result:
            raise EmbeddingUnavailable("empty response")
        return result[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        url = f"{self.base_url}/api/embed"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    url, json={"model": self.model, "input": texts}
                )
                if resp.status_code >= 400:
                    raise EmbeddingUnavailable(
                        f"ollama embed {resp.status_code}: {resp.text[:200]}"
                    )
                data = resp.json()
        except httpx.RequestError as exc:
            raise EmbeddingUnavailable(f"ollama unreachable: {exc}") from exc

        # Newer Ollama returns "embeddings"; some versions return "embedding".
        emb = data.get("embeddings") or (
            [data["embedding"]] if "embedding" in data else None
        )
        if not emb:
            raise EmbeddingUnavailable(f"unexpected response: {data}")
        return emb


_singleton: Optional[EmbeddingClient] = None


def get_embedding_client() -> EmbeddingClient:
    global _singleton
    if _singleton is None:
        _singleton = EmbeddingClient()
    return _singleton
