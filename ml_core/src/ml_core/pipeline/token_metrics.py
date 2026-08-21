"""Token counting helpers for summarizer input comparison."""

from __future__ import annotations

import json
from typing import Any


def estimate_token_count(text: str) -> int:
    """
    Estimate token count for LLM input.

    Uses tiktoken when available; otherwise falls back to a chars/4 heuristic
    (typical for English clinical text with BPE tokenizers).
    """
    if not text:
        return 0

    try:
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        return max(1, len(text) // 4)


def build_summarizer_payload(diseases: list[dict], labs: list[dict]) -> str:
    """Canonical JSON payload sent to the summarizer (user message body)."""
    return json.dumps(
        {"diseases_json": diseases, "labs_json": labs},
        ensure_ascii=False,
    )


def build_summarizer_token_metrics(
    extracted_text: str,
    diseases: list[dict[str, Any]],
    labs: list[dict[str, Any]],
    *,
    system_prompt: str = "",
) -> dict[str, Any]:
    """
    Compare tokens for naive whole-document summarization vs structured input.

    Returns counts for the summarizer LLM only (system prompt + user content).
    """
    structured_payload = build_summarizer_payload(diseases, labs)
    whole_document_payload = extracted_text or ""

    system_tokens = estimate_token_count(system_prompt)
    whole_document_tokens = system_tokens + estimate_token_count(whole_document_payload)
    summarizer_input_tokens = system_tokens + estimate_token_count(structured_payload)
    tokens_saved = max(whole_document_tokens - summarizer_input_tokens, 0)
    reduction_percent = (
        round((tokens_saved / whole_document_tokens) * 100, 2)
        if whole_document_tokens
        else 0.0
    )

    return {
        "whole_document_tokens": whole_document_tokens,
        "summarizer_input_tokens": summarizer_input_tokens,
        "tokens_saved": tokens_saved,
        "reduction_percent": reduction_percent,
    }
