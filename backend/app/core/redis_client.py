"""Thin Redis wrapper used for caching AI results and rate limiting."""
import json
from typing import Any, Optional

import redis

from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def cache_get(key: str) -> Optional[Any]:
    raw = redis_client.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def cache_set(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    payload = value if isinstance(value, str) else json.dumps(value)
    redis_client.set(key, payload, ex=ttl_seconds)


def cache_delete(key: str) -> None:
    redis_client.delete(key)
