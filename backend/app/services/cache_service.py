"""
Caches AI (LLM) results in Redis so identical summary/explanation requests
don't re-hit Ollama. Keyed by a hash of the exact inputs that go into the
prompt, so the cache is automatically invalidated whenever the underlying
endpoint/project content actually changes -- no manual cache-busting needed.

Deliberately fails open: if Redis is briefly unavailable, callers should
just fall through to calling the LLM directly rather than erroring out.
"""
import hashlib
import json
import logging
from typing import Any, Optional

from app.core.config import settings
from app.core.redis_client import cache_get, cache_set

logger = logging.getLogger(__name__)

_NAMESPACE = "ai_cache"


def build_cache_key(kind: str, payload: Any) -> str:
    """Builds a stable cache key from a JSON-serializable payload. Using a
    content hash (rather than e.g. project id) means the cache entry is
    naturally invalidated the moment the underlying endpoints/description
    change, without needing an explicit invalidation step."""
    serialized = json.dumps(payload, sort_keys=True, default=str)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"{_NAMESPACE}:{kind}:{digest}"


def get_cached_ai_result(kind: str, payload: Any) -> Optional[str]:
    key = build_cache_key(kind, payload)
    try:
        value = cache_get(key)
    except Exception:
        logger.warning("AI cache read failed for kind=%s; falling through to live call", kind)
        return None
    if value is None:
        return None
    logger.info("AI cache hit for kind=%s", kind)
    return value if isinstance(value, str) else json.dumps(value)


def set_cached_ai_result(kind: str, payload: Any, result: str) -> None:
    key = build_cache_key(kind, payload)
    try:
        cache_set(key, result, ttl_seconds=settings.AI_CACHE_TTL_SECONDS)
    except Exception:
        # Caching is a performance optimization, not a correctness
        # requirement -- never let a Redis hiccup break an AI response
        # the user is actively waiting on.
        logger.warning("AI cache write failed for kind=%s", kind)
