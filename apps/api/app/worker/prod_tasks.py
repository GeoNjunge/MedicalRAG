"""Production job processing without Redis RQ workers."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.core.logger_setup import CentralizedLogger
from app.core.audit_logger import log_job_terminal
from app.database.session import SessionLocal
from app.models.job import Job
from app.services.file_cleanup import delete_upload_file
from app.services.job_events import job_event_bus
from ml_core.pipeline.prod_pipeline import run_prod_pipeline

logger = CentralizedLogger.get_logger(__name__)


def _stage_from_status(status_text: str | dict) -> str:
    if isinstance(status_text, dict):
        return "completed"

    if not isinstance(status_text, str):
        return "processing"

    normalized = status_text.lower()
    if "extracting text" in normalized:
        return "extract_text"
    if "chunking text" in normalized:
        return "chunk_text"
    if "cleaning" in normalized:
        return "clean_text"
    if "extracting diseases" in normalized:
        return "extract_diseases"
    if "extracting lab" in normalized:
        return "extract_labs"
    if "generating summary" in normalized:
        return "summarize"
    if "failed" in normalized:
        return "failed"
    return "processing"


def _publish_status(job_id: str, status_text: str | dict) -> None:
    event_type = "progress"
    if isinstance(status_text, dict):
        event_type = "completed"
    elif isinstance(status_text, str) and status_text.lower() == "failed":
        event_type = "failed"

    event_payload = {
        "type": event_type,
        "job_id": str(job_id),
        "stage": _stage_from_status(status_text),
        "status": status_text if not isinstance(status_text, dict) else "Completed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if isinstance(status_text, dict):
        event_payload["result"] = status_text

    job_event_bus.publish(job_id, event_payload)
    logger.info(f"Job {job_id} status: {status_text}")


def _process_prod_job_sync(job_id: str, file_path: str) -> None:
    db = None
    job = None
    try:
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == str(job_id)).first()
        if not job:
            raise RuntimeError("Job not found")

        job.started_at = datetime.now(timezone.utc)
        job.status = "processing"
        db.commit()

        with open(file_path, "rb") as file_handle:
            file_bytes = file_handle.read()

        _publish_status(job_id, "Worker has started processing doc")

        result = run_prod_pipeline(
            file_bytes,
            job.original_filename,
            on_status=lambda status: _publish_status(job_id, status),
        )

        if "error" in result:
            job.error_message = result["error"]
            job.status = "failed"
            job.retry_count += 1
            db.commit()
            log_job_terminal(str(job.id), "failed", patient_id=job.patient_id)
            return

        job.diseases_json = result["diseases_json"]
        job.extracted_text = result["extracted_text"]
        job.labs_json = result["labs_json"]
        job.summary_text = result["summary_text"]
        job.token_metrics_json = result.get("token_metrics")
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        log_job_terminal(str(job.id), "completed", patient_id=job.patient_id)
        logger.info(f"Job {job.id} completed at {job.completed_at}")
    except Exception as error:
        logger.error(f"Production pipeline failed for job {job_id}: {error}")
        _publish_status(job_id, "Failed")
        if job is not None:
            job.status = "failed"
            job.retry_count += 1
            job.error_message = str(error)
            db.commit()
            log_job_terminal(str(job.id), "failed", patient_id=job.patient_id)
        raise
    finally:
        delete_upload_file(file_path)
        if db is not None:
            db.close()


async def _run_prod_job(job_id: str, file_path: str) -> None:
    await asyncio.to_thread(_process_prod_job_sync, job_id, file_path)


def schedule_prod_job(job_id: str, file_path: str) -> asyncio.Task:
    return asyncio.create_task(_run_prod_job(job_id, file_path))
