"""SQLAlchemy column types that transparently encrypt/decrypt PHI at rest."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.types import Text, TypeDecorator

from app.core.security_encryption import decrypt_field, encrypt_field


class EncryptedString(TypeDecorator):
    """Encrypt string values before writing to the database."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        if value is None:
            return None
        return encrypt_field(str(value))

    def process_result_value(self, value: str | None, dialect) -> str | None:
        if value is None:
            return None
        return decrypt_field(value)


class EncryptedJSON(TypeDecorator):
    """Encrypt JSON-serializable values as an encrypted text blob."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any, dialect) -> str | None:
        if value is None:
            return None
        serialized = json.dumps(value, ensure_ascii=False)
        return encrypt_field(serialized)

    def process_result_value(self, value: str | None, dialect) -> Any:
        if value is None:
            return None
        decrypted = decrypt_field(value)
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return decrypted
