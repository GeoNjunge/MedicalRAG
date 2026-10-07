"""API rate limiting (Redis-backed when available, in-memory fallback)."""

from __future__ import annotations

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import config


def rate_limit_key(request: Request) -> str:
    api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    if api_key:
        return f"api_key:{api_key.strip()}"

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    return get_remote_address(request)


def _storage_uri() -> str:
    if config.REDIS_URL:
        return config.REDIS_URL
    return "memory://"


limiter = Limiter(
    key_func=rate_limit_key,
    storage_uri=_storage_uri(),
    default_limits=[],
)
