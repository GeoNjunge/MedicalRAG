from fastapi import UploadFile
from typing import Optional
from app.services.file_validation import validator
from app.storage.s3 import uploader
from sqlalchemy.orm import Session
from app.core.logger_setup import logger, CentralizedLogger
from app.models.job import Job
from app.queue.job_queue import queue

logger = CentralizedLogger.get_logger(__name__)


def push_job(job_id):
    try:
        logger.info(f"--- ATTEMPTING REDIS ENQUEUE FOR {job_id} ---")
        # Use the string path to avoid import errors
        enqueued_job = queue.enqueue(
            "app.worker.tasks.process_ai_job", 
            args=(str(job_id),),
            job_id=str(job_id)
        )
        logger.info(f"--- SUCCESS: Job {enqueued_job.id} is now in Redis ---")
        return enqueued_job
    except Exception as e:
        logger.error(f"!!! REDIS ENQUEUE FAILED: {e} !!!")
        raise


async def upload_file(file: UploadFile,
        patient_id: str,
        priority: int,
        model_version: Optional[str],
        db: Session):
    
    try:
        #Validator
        validator.validate_size(file)
        await validator.validate_pdf(file)

        # Compute Hash
        file_hash = validator.compute_hash(file)

        # Upload to S3
        result = await uploader.upload_file_to_s3(file, patient_id)

        # Job ORM object creation
        job = Job(
            patient_id=patient_id,
            input_type="pdf",
            file_url=result["object_url"],
            original_filename=result["filename"],
            priority=priority,
            model_version=model_version,
            file_hash=file_hash
        )

        logger.info("Creating Job...")

        # Save
        db.add(job)
        db.commit()
        # 1. Store the ID as a plain string immediately
        # This avoids issues if refresh() hangs
        job_id_str = str(job.id)
        
        try:
            db.refresh(job)
            logger.info(f"Job refreshed. ID: {job_id_str}")
        except Exception as e:
            logger.warning(f"Refresh failed but continuing: {e}")
        # Push job_id to queue
        push_job(job.id)

        # Return 
        return {"job_id": job.id, "job_status":job.status, "message":"Job Created Successfully"}

    except Exception as error:
        logger.error(f"Error Uploading file: {error}")
        db.rollback()
        raise