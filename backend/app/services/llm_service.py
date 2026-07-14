"""
Wraps calls to whichever LLM backend is configured (LLM_PROVIDER):

- "ollama": a self-hosted Ollama server (free, fully local, but needs a
  reasonably powerful machine -- CPU-only inference of a 7B model can take
  minutes per response).
- "groq": Groq's hosted inference API (free tier, no local compute needed,
  responses typically return in 1-3 seconds).

Centralizing both behind the same generate()/stream_generate() interface
means the rest of the app (analysis_service, rag_service) never needs to
know which provider is active -- only this file branches on it.
"""
import json
import logging
from typing import AsyncGenerator, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMUnavailableError(Exception):
    """Raised when the configured LLM backend cannot be reached or errors out."""


async def generate(prompt: str, system: Optional[str] = None, temperature: float = 0.3) -> str:
    """Single-shot (non-streaming) completion. Used for summaries, risk
    reports, and code generation where we need the full text at once."""
    if settings.LLM_PROVIDER == "groq":
        return await _groq_generate(prompt, system, temperature)
    return await _ollama_generate(prompt, system, temperature)


async def stream_generate(prompt: str, system: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Streams tokens back as they're generated, for the AI Chat page."""
    if settings.LLM_PROVIDER == "groq":
        async for token in _groq_stream(prompt, system):
            yield token
        return
    async for token in _ollama_stream(prompt, system):
        yield token


# --------------------------------------------------------------------------
# Ollama
# --------------------------------------------------------------------------

async def _ollama_generate(prompt: str, system: Optional[str], temperature: float) -> str:
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "system": system or "",
        "stream": False,
        "options": {"temperature": temperature},
    }
    try:
        async with httpx.AsyncClient(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{settings.OLLAMA_BASE_URL}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
    except httpx.HTTPError as exc:
        logger.error("Ollama request failed: %s", exc)
        raise LLMUnavailableError(str(exc)) from exc


async def _ollama_stream(prompt: str, system: Optional[str]) -> AsyncGenerator[str, None]:
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "system": system or "",
        "stream": True,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as client:
            async with client.stream("POST", f"{settings.OLLAMA_BASE_URL}/api/generate", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break
    except httpx.HTTPError as exc:
        logger.error("Ollama streaming request failed: %s", exc)
        yield f"\n[AI service unavailable: {exc}]"


# --------------------------------------------------------------------------
# Groq (OpenAI-compatible chat completions API)
# --------------------------------------------------------------------------

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _groq_headers() -> dict:
    if not settings.GROQ_API_KEY:
        raise LLMUnavailableError(
            "LLM_PROVIDER is set to 'groq' but GROQ_API_KEY is empty. "
            "Get a free key at https://console.groq.com and set it in your environment."
        )
    return {"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"}


def _groq_messages(prompt: str, system: Optional[str]) -> list[dict]:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return messages


async def _groq_generate(prompt: str, system: Optional[str], temperature: float) -> str:
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": _groq_messages(prompt, system),
        "temperature": temperature,
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(_GROQ_URL, json=payload, headers=_groq_headers())
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except httpx.HTTPError as exc:
        logger.error("Groq request failed: %s", exc)
        raise LLMUnavailableError(str(exc)) from exc


async def _groq_stream(prompt: str, system: Optional[str]) -> AsyncGenerator[str, None]:
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": _groq_messages(prompt, system),
        "stream": True,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS) as client:
            async with client.stream("POST", _GROQ_URL, json=payload, headers=_groq_headers()) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[len("data: "):]
                    if data_str.strip() == "[DONE]":
                        break
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0].get("delta", {})
                    token = delta.get("content")
                    if token:
                        yield token
    except httpx.HTTPError as exc:
        logger.error("Groq streaming request failed: %s", exc)
        yield f"\n[AI service unavailable: {exc}]"
