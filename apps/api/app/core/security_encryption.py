"""Field-level PHI encryption using Fernet symmetric encryption."""

from __future__ import annotations

import os

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import config, is_production
from app.core.logger_setup import CentralizedLogger

logger = CentralizedLogger.get_logger(__name__)

_fernet: Fernet | None = None


def _resolve_encryption_key() -> str | None:
    return (os.getenv("ENCRYPTION_KEY") or config.ENCRYPTION_KEY or "").strip() or None


def _get_fernet() -> Fernet | None:
    global _fernet
    if _fernet is not None:
        return _fernet

    key = _resolve_encryption_key()
    if not key:
        if is_production():
            raise RuntimeError("ENCRYPTION_KEY must be set when APP_ENV is production.")
        logger.warning("ENCRYPTION_KEY not set; PHI fields will be stored in plaintext (dev only)")
        return None

    _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def reset_encryption_client() -> None:
    """Reset cached Fernet client (used in tests)."""
    global _fernet
    _fernet = None


def encrypt_field(data: str) -> str:
    """Encrypt a string value for database persistence."""
    if data is None:
        return data

    fernet = _get_fernet()
    if fernet is None:
        return data

    return fernet.encrypt(data.encode("utf-8")).decode("utf-8")


def decrypt_field(token: str) -> str:
    """Decrypt a persisted token; returns legacy plaintext when decryption fails."""
    if token is None:
        return token

    fernet = _get_fernet()
    if fernet is None:
        return token

    try:
        return fernet.decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        # Backward compatibility for rows written before encryption was enabled.
        return token
