from pathlib import Path
import re

from fastapi import Depends, HTTPException, UploadFile
from typing import Optional
from app.services.file_validation import validator
from app.storage.s3 import uploader
from sqlalchemy.orm import Session
from app.core.logger_setup import CentralizedLogger
from app.models.job import Job
from app.core.config import is_production
from app.database.session import get_db
from app.services.file_cleanup import delete_upload_file

logger = CentralizedLogger.get_logger(__name__)

_PATIENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _validate_patient_id(patient_id: str) -> None:
    if not _PATIENT_ID_PATTERN.match(patient_id):
        raise HTTPException(
            status_code=400,
            detail="patient_id must be 1-64 alphanumeric characters, hyphens, or underscores",
        )


def _sanitize_filename(filename: str | None) -> str:
    if not filename:
        return "upload.pdf"
    safe_name = Path(filename).name
    if safe_name in {"", ".", ".."} or ".." in safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    return safe_name


async def upload_file(
    file: UploadFile,
    patient_id: str,
    priority: int,
    model_version: Optional[str],
    db: Session = Depends(get_db),
):
    try:
        _validate_patient_id(patient_id)
        safe_filename = _sanitize_filename(file.filename)

        validator.validate_size(file)
        await validator.validate_pdf(file)

        # Compute Hash
        file_hash = validator.compute_hash(file)

        unique_key = uploader.get_s3_key(safe_filename, patient_id)
        file_path = Path(f"files/{unique_key}")
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
            
        # Job ORM object creation
        job = Job(
            patient_id=patient_id,
            input_type="pdf",
            file_url="object_url",
            original_filename=safe_filename,
            priority=priority,
            model_version=model_version,
            file_hash=file_hash,
            file_path=str(file_path)
        )

        logger.info("Creating Job...")

        # Save
        db.add(job)
        db.commit()
        job_id_str = str(job.id)

        try:
            db.refresh(job)
            logger.info(f"Job refreshed. ID: {job_id_str}")
        except Exception as e:
            logger.warning(f"Refresh failed but continuing: {e}")

        try:
            if is_production():
                from app.worker.prod_tasks import schedule_prod_job

                schedule_prod_job(job.id, job.file_path)
                logger.info(f"Scheduled production pipeline for job {job_id_str}")
            else:
                from app.services.push_job_to_redis import push_job

                push_job(job.id, job.file_path)
                logger.info(f"Enqueued development pipeline for job {job_id_str}")
        except Exception as enqueue_error:
            logger.error(f"Failed to enqueue job {job_id_str}: {enqueue_error}")
            job.status = "failed"
            job.error_message = f"Enqueue failed: {enqueue_error}"
            db.commit()
            delete_upload_file(file_path)
            raise HTTPException(
                status_code=503,
                detail="Failed to enqueue job for processing",
            ) from enqueue_error

        return {"job_id": job.id, "job_status": job.status, "message": "Job Created Successfully"}

    except Exception as error:
        logger.error(f"Error Uploading file: {error}")
        db.rollback()
        raise
