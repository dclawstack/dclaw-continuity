"""LLM client with OpenRouter primary + Ollama fallback.

Both backends speak the OpenAI chat-completions shape. Ollama exposes it at
`/v1/chat/completions`; OpenRouter exposes it at `/chat/completions`.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


class LLMError(RuntimeError):
    pass


class LLMClient:
    """Async client. Tries OpenRouter, falls back to Ollama on failure."""

    def __init__(
        self,
        *,
        openrouter_api_key: str | None = None,
        openrouter_base_url: str | None = None,
        openrouter_model: str | None = None,
        ollama_base_url: str | None = None,
        ollama_model: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.openrouter_api_key = openrouter_api_key or settings.openrouter_api_key
        self.openrouter_base_url = (openrouter_base_url or settings.openrouter_base_url).rstrip("/")
        self.openrouter_model = openrouter_model or settings.openrouter_model
        self.ollama_base_url = (ollama_base_url or settings.ollama_base_url).rstrip("/")
        self.ollama_model = ollama_model or settings.ollama_model
        self.timeout = timeout or settings.llm_request_timeout

    async def chat(
        self,
        messages: Iterable[ChatMessage | dict[str, str]],
        *,
        json_mode: bool = False,
        temperature: float = 0.2,
    ) -> str:
        payload_msgs = [m.to_dict() if isinstance(m, ChatMessage) else dict(m) for m in messages]

        if self.openrouter_api_key:
            try:
                return await self._openrouter(
                    payload_msgs, json_mode=json_mode, temperature=temperature
                )
            except Exception as exc:
                log.warning("openrouter_call_failed_falling_back_to_ollama", error=str(exc))

        try:
            return await self._ollama(payload_msgs, json_mode=json_mode, temperature=temperature)
        except Exception as exc:
            raise LLMError(f"all llm backends failed: {exc}") from exc

    async def chat_json(
        self,
        messages: Iterable[ChatMessage | dict[str, str]],
        *,
        temperature: float = 0.2,
    ) -> Any:
        raw = await self.chat(messages, json_mode=True, temperature=temperature)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            cleaned = _strip_fences(raw)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                raise LLMError(f"llm returned non-JSON: {raw[:200]}") from exc

    async def _openrouter(
        self,
        messages: list[dict[str, str]],
        *,
        json_mode: bool,
        temperature: float,
    ) -> str:
        # NOTE: Not all OpenRouter models support OpenAI's `response_format` —
        # e.g. moonshotai/kimi-k2 rejects it. The prompts themselves demand
        # JSON, and chat_json() strips code fences if the model wraps the body.
        url = f"{self.openrouter_base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.openrouter_model,
            "messages": messages,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if resp.status_code >= 400:
                raise LLMError(f"openrouter {resp.status_code}: {resp.text[:300]}")
            data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def _ollama(
        self,
        messages: list[dict[str, str]],
        *,
        json_mode: bool,
        temperature: float,
    ) -> str:
        # CPU-bound ollama can be very slow; cap response length so the call
        # finishes inside the proxy's tolerance, and ask ollama to keep the
        # model resident so subsequent turns skip the cold-load cost.
        url = f"{self.ollama_base_url}/v1/chat/completions"
        payload: dict[str, Any] = {
            "model": self.ollama_model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
            "max_tokens": settings.ollama_max_tokens,
            "keep_alive": settings.ollama_keep_alive,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]


def _strip_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s[3:]
        if s.endswith("```"):
            s = s[:-3]
    return s.strip()


_singleton: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _singleton
    if _singleton is None:
        _singleton = LLMClient()
    return _singleton
