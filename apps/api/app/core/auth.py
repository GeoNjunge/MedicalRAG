"""API authentication dependencies."""

from __future__ import annotations

from fastapi import Header, HTTPException, Query, status

from app.core.config import config, is_production


def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    api_key: str | None = Query(default=None),
) -> None:
    """
    Require a shared API key in production.

    SSE (EventSource) cannot set custom headers in browsers, so callers may pass
    `api_key` as a query parameter on GET endpoints only.
    """
    if not is_production():
        return

    expected = (config.API_KEY or "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_KEY is not configured on the server",
        )

    provided = (x_api_key or api_key or "").strip()
    if not provided or provided != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
