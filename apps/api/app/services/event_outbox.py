from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.logger_setup import CentralizedLogger
from app.database.session import SessionLocal
from app.models.job_event_outbox import JobEventOutbox

logger = CentralizedLogger.get_logger(__name__)

CHANNEL_PREFIX = "job_events:"


def _redis_client():
    from app.queue.redis_client import redis_conn

    return redis_conn


def _publish_to_redis(job_id: str, event: dict[str, Any]) -> None:
    channel = f"{CHANNEL_PREFIX}{job_id}"
    _redis_client().publish(channel, json.dumps(event, default=str))


def persist_job_event(db: Session, job_id: str, event: dict[str, Any]) -> JobEventOutbox:
    row = JobEventOutbox(
        job_id=str(job_id),
        event_type=str(event.get("type", "progress")),
        payload_json=event,
        published=False,
    )
    db.add(row)
    db.flush()
    return row


def mark_event_published(db: Session, row: JobEventOutbox) -> None:
    row.published = True
    row.published_at = datetime.now(timezone.utc)
    row.publish_error = None
    db.add(row)


def publish_job_event(
    job_id: str,
    event: dict[str, Any],
    db: Session | None = None,
    *,
    commit: bool = True,
) -> JobEventOutbox | None:
    """
    Transactionally persist a job event, then dispatch to Redis Pub/Sub.

    If Redis is temporarily unavailable the row remains unpublished and will be
    replayed by `replay_unpublished_events()` on startup.
    """
    own_session = False
    session = db
    if session is None:
        session = SessionLocal()
        own_session = True

    row: JobEventOutbox | None = None
    try:
        row = persist_job_event(session, job_id, event)
        if commit:
            session.commit()

        try:
            _publish_to_redis(job_id, event)
        except Exception as exc:
            logger.warning("Redis publish failed for job %s: %s", job_id, exc)
            if row is not None:
                row.publish_error = str(exc)
                session.add(row)
                if commit:
                    session.commit()
            return row

        if row is not None:
            mark_event_published(session, row)
            if commit:
                session.commit()
        return row
    finally:
        if own_session:
            session.close()


def replay_unpublished_events(limit: int = 500) -> int:
    """Replay outbox rows that were never successfully published to Redis."""
    db = SessionLocal()
    dispatched = 0
    try:
        rows = (
            db.query(JobEventOutbox)
            .filter(JobEventOutbox.published.is_(False))
            .order_by(JobEventOutbox.created_at.asc())
            .limit(limit)
            .all()
        )
        for row in rows:
            try:
                _publish_to_redis(row.job_id, row.payload_json)
                mark_event_published(db, row)
                dispatched += 1
            except Exception as exc:
                row.publish_error = str(exc)
                db.add(row)
                logger.warning(
                    "Outbox replay failed for job %s event %s: %s",
                    row.job_id,
                    row.id,
                    exc,
                )
        db.commit()
    finally:
        db.close()

    if dispatched:
        logger.info("Replayed %d unpublished job event(s) from outbox", dispatched)
    return dispatched


def latest_published_event(job_id: str) -> dict[str, Any] | None:
    """Return the most recent published event for SSE reconnect hydration."""
    db = SessionLocal()
    try:
        row = (
            db.query(JobEventOutbox)
            .filter(
                JobEventOutbox.job_id == str(job_id),
                JobEventOutbox.published.is_(True),
            )
            .order_by(JobEventOutbox.created_at.desc())
            .first()
        )
        return row.payload_json if row is not None else None
    finally:
        db.close()
