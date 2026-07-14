"""
Simple fixed-window rate limiter backed by Redis. Applied per client IP.
This is intentionally simple (fixed window, not sliding/token-bucket) so
it's easy to explain in an interview while still being genuinely effective.
"""
import time

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.redis_client import redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api"):
            client_ip = request.client.host if request.client else "unknown"
            window = int(time.time() // 60)
            key = f"ratelimit:{client_ip}:{window}"

            try:
                current = redis_client.incr(key)
                if current == 1:
                    redis_client.expire(key, 60)
                if current > settings.RATE_LIMIT_PER_MINUTE:
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={"detail": "Rate limit exceeded. Please slow down."},
                    )
            except Exception:
                # If Redis is briefly unavailable, fail open rather than
                # blocking all traffic.
                pass

        return await call_next(request)
