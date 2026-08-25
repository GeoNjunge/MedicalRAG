from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models.job_event_outbox import JobEventOutbox

logger = logging.getLogger("audit")


def _ensure_audit_handler() -> None:
    audit_path = Path("logs/audit.log")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    if any(isinstance(handler, logging.FileHandler) and handler.baseFilename.endswith("audit.log") for handler in logger.handlers):
        return

    handler = logging.FileHandler(audit_path)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


_ensure_audit_handler()


def _client_ip(request: Any | None) -> str | None:
    if request is None:
        return None
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return None


def log_audit_event(
    *,
    event_type: str,
    job_id: str | None = None,
    patient_id: str | None = None,
    status: str | None = None,
    client_ip: str | None = None,
    request: Any | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """
    Emit a structured JSON audit record for HIPAA/security traceability.

    Avoids logging raw PHI content (extracted text, summaries, file bytes).
    """
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "job_id": job_id,
        "patient_id": patient_id,
        "status": status,
        "client_ip": client_ip or _client_ip(request),
    }
    if extra:
        record.update(extra)

    logger.info(json.dumps(record, default=str))


def log_upload_created(request: Any, job_id: str, patient_id: str, status: str) -> None:
    log_audit_event(
        event_type="upload_created",
        job_id=job_id,
        patient_id=patient_id,
        status=status,
        request=request,
    )


def log_job_status_fetched(request: Any, job_id: str, status: str) -> None:
    log_audit_event(
        event_type="job_status_fetched",
        job_id=job_id,
        status=status,
        request=request,
    )


def log_sse_connected(request: Any, job_id: str, status: str) -> None:
    log_audit_event(
        event_type="sse_connected",
        job_id=job_id,
        status=status,
        request=request,
    )


def log_job_terminal(job_id: str, status: str, patient_id: str | None = None) -> None:
    event_type = "job_completed" if status == "completed" else "job_failed"
    log_audit_event(
        event_type=event_type,
        job_id=job_id,
        patient_id=patient_id,
        status=status,
    )
