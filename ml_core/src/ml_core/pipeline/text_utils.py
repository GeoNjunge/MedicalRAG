"""Text helpers shared across pipeline modules."""

from __future__ import annotations

import re


def strip_markdown(text: str) -> str:
    """Remove common markdown formatting from LLM output."""
    cleaned = text.strip()
    cleaned = re.sub(r"^#{1,6}\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"^[-*+]\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\d+\.\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"```.*?```", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
