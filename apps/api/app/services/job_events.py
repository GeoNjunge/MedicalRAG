"""Job event bus for SSE progress streaming (Redis Pub/Sub with in-memory fallback)."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

from ml_core.logging_utils import CentralizedLogger

logger = CentralizedLogger.get_logger(__name__)

CHANNEL_PREFIX = "job_events:"


class InMemoryJobEventBus:
    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue[dict[str, Any]]] = {}
        self._latest: dict[str, dict[str, Any]] = {}

    def publish(self, job_id: str, event: dict[str, Any]) -> None:
        self._latest[job_id] = event
        queue = self._queues.get(job_id)
        if queue is not None:
            queue.put_nowait(event)

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


class RedisJobEventBus:
    def __init__(self, redis_conn) -> None:
        self._redis = redis_conn

    def publish(self, job_id: str, event: dict[str, Any]) -> None:
        channel = f"{CHANNEL_PREFIX}{job_id}"
        self._redis.publish(channel, json.dumps(event, default=str))

    async def subscribe(self, job_id: str) -> AsyncIterator[dict[str, Any]]:
        pubsub = self._redis.pubsub()
        channel = f"{CHANNEL_PREFIX}{job_id}"
        pubsub.subscribe(channel)

        try:
            while True:
                message = await asyncio.to_thread(
                    pubsub.get_message,
                    ignore_subscribe_messages=True,
                    timeout=1.0,
                )
                if message and message.get("type") == "message":
                    raw_data = message.get("data")
                    if isinstance(raw_data, bytes):
                        raw_data = raw_data.decode("utf-8")
                    try:
                        event = json.loads(raw_data)
                    except json.JSONDecodeError:
                        logger.warning("Invalid JSON on job event channel %s", job_id)
                        continue

                    yield event
                    if event.get("type") in {"completed", "failed"}:
                        break
                else:
                    yield {"type": "ping"}
        finally:
            pubsub.unsubscribe(channel)
            pubsub.close()

    def clear(self, job_id: str) -> None:
        return


def _build_job_event_bus():
    try:
        from app.queue.redis_client import redis_conn

        redis_conn.ping()
        logger.info("Job events using Redis Pub/Sub")
        return RedisJobEventBus(redis_conn)
    except Exception as exc:
        from app.core.config import is_production

        if is_production():
            logger.warning(
                "Redis unavailable in production (%s); falling back to in-memory bus "
                "(not safe for multiple workers)",
                exc,
            )
        else:
            logger.info("Redis unavailable (%s); using in-memory job event bus", exc)
        return InMemoryJobEventBus()


job_event_bus = _build_job_event_bus()
