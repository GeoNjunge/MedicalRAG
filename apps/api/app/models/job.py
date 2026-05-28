from sqlalchemy import String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import uuid

from app.database.base import Base

class Job(Base):
    __tablename__ = "jobs"

    # Identity
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(String, nullable=False)

    # Input metadata
    input_type: Mapped[str] = mapped_column(String, nullable=False)
    file_url: Mapped[str] = mapped_column(String, nullable=True)
    original_filename: Mapped[str] = mapped_column(String, nullable=True)
    file_hash: Mapped[str] = mapped_column(String, nullable=True)
    file_path: Mapped[str] = mapped_column(String, nullable=True, unique=True)

    # State management
    status: Mapped[str] = mapped_column(String, default="pending", index=True)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)

    # Processing info
    model_version: Mapped[str] = mapped_column(String, nullable=True)
    worker_id: Mapped[str] = mapped_column(String, nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Partial results
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    diseases_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    labs_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    summary_text: Mapped[str] = mapped_column(Text, nullable=True)

    # Errors
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    last_retry_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Observability
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default= lambda: datetime.now(timezone.utc), onupdate= lambda: datetime.now(timezone.utc)
    )
