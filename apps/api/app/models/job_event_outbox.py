from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class JobEventOutbox(Base):
    """Durable outbox for job status events prior to Redis Pub/Sub dispatch."""

    __tablename__ = "job_event_outbox"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    publish_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
