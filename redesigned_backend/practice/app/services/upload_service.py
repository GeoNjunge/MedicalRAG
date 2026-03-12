from practice.app.services.file_validation import validation_cls
from practice.app.storage.s3 import uploader
from practice.app.database.init_db import get_db
from sqlalchemy.orm import Session
from fastapi import UploadFile
from practice.app.models.job import Job
from practice.app.config.logger_setup import CentralizedLogger, logger
from practice.app.worker.worker import queue
from practice.app.worker.tasks import process_ai_job

logger = CentralizedLogger.get_logger(__name__)

def push_job(job_id):
    try:
        logger.info(f"Trying to queue job")

        enqueued_job = queue.enqueue(
            "practice.app.worker.tasks.process_ai_job",
            args=(str(job_id),),
            job_id = str(job_id)
        )
        logger.info(f"--- SUCCESS: Job {enqueued_job.id} is now in Redis ---")
        return enqueued_job
    except Exception as e:
        logger.error(f"!!! REDIS ENQUEUE FAILED: {e} !!!")
        raise
        

async def upload_service(
        file: UploadFile,
        patient_id: str,
        priority: int, 
        model_version: str,
        db: Session
):
    try:
        # validation
        validation_cls.validate_size(file)
        await validation_cls.validate_pdf(file)

        hash = validation_cls.compute_hash(file)

        # Upload to S3
        result = await uploader.upload_to_s3(file, patient_id)

        # Store to db
        job = Job(
            patient_id=patient_id,
            input_type = "pdf",
            file_url = result["object_url"],
            original_filename = result["filename"],
            file_hash = hash,
            priority = priority,
            model_version = model_version,
        )

        logger.info("Creating job...")

        db.add(job)
        db.commit()

        job_id = str(job.id)

        try:
            db.refresh(job)
            logger.info(f"Job refreshed: {job_id}")

        except Exception as e:
            logger.warning(f"Job failed to refresh but continuing: {job_id}")
            raise

        push_job(job_id)

         # Return 
        return {"job_id": str(job.id), "job_status":str(job.status), "message":"Job Created Successfully"}
    except Exception as e:
        logger.error(f"Failed to upload file and create job: {e}")
        db.rollback()
        raise
