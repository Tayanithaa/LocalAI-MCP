"""
Thin async client for a local Ollama server. Ollama's /api/chat endpoint
speaks an OpenAI-ish JSON schema, so this stays deliberately small rather
than pulling in a heavy SDK for two endpoints.
"""
from __future__ import annotations

import json
from typing import Any

import httpx

from config.settings import settings
from config.logger import get_logger

log = get_logger("ollama.client")


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, host: str | None = None, model: str | None = None):
        self.host = (host or settings.ollama_host).rstrip("/")
        self.model = model or settings.ollama_model

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        json_mode: bool = False,
        temperature: float = 0.2,
    ) -> str:
        """Send a chat completion request and return the assistant's text content."""
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if json_mode:
            payload["format"] = "json"

        url = f"{self.host}/api/chat"
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
        except httpx.ConnectError as e:
            raise OllamaError(
                f"Could not reach Ollama at {self.host}. Is `ollama serve` running "
                f"and is '{self.model}' pulled (`ollama pull {self.model}`)?"
            ) from e
        except httpx.HTTPStatusError as e:
            raise OllamaError(f"Ollama returned {e.response.status_code}: {e.response.text}") from e

        data = resp.json()
        content = data.get("message", {}).get("content", "")
        if not content:
            raise OllamaError(f"Empty response from Ollama: {json.dumps(data)[:300]}")
        return content
