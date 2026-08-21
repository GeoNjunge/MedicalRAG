"""Character-based sliding windows for bounded NER / medSpaCy passes."""

from __future__ import annotations

from collections.abc import Iterator

DEFAULT_WINDOW_SIZE = 512
DEFAULT_WINDOW_OVERLAP = 64
LAB_TOKEN_WINDOW = 10


def iter_sliding_windows(
    text: str,
    window_size: int = DEFAULT_WINDOW_SIZE,
    overlap: int = DEFAULT_WINDOW_OVERLAP,
) -> Iterator[tuple[int, str]]:
    """Yield `(char_offset, window_text)` slices over *text*."""
    if not text or not text.strip():
        return

    if len(text) <= window_size:
        yield 0, text
        return

    step = max(window_size - overlap, 1)
    start = 0
    while start < len(text):
        end = min(start + window_size, len(text))
        window = text[start:end]
        if window.strip():
            yield start, window
        if end >= len(text):
            break
        start += step
