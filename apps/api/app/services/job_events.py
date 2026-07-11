"""In-memory job event bus for production SSE (no Redis required)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any


class JobEventBus:
    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue[dict[str, Any]]] = {}
        self._latest: dict[str, dict[str, Any]] = {}

    def publish(self, job_id: str, event: dict[str, Any]) -> None:
        self._latest[job_id] = event
        queue = self._queues.get(job_id)
        if queue is not None:
            queue.put_nowait(event)

    def get_latest(self, job_id: str) -> dict[str, Any] | None:
        return self._latest.get(job_id)

    async def subscribe(self, job_id: str) -> AsyncIterator[dict[str, Any]]:
        queue = self._queues.setdefault(job_id, asyncio.Queue())
        latest = self._latest.get(job_id)
        if latest is not None:
            yield latest
            if latest.get("type") in {"completed", "failed"}:
                return

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                yield {"type": "ping"}
                continue

            yield event
            if event.get("type") in {"completed", "failed"}:
                break

    def clear(self, job_id: str) -> None:
        self._latest.pop(job_id, None)
        self._queues.pop(job_id, None)


job_event_bus = JobEventBus()
