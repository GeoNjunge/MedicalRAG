from pathlib import Path

from fastapi import Depends, UploadFile
from typing import Optional
from app.services.file_validation import validator
from app.storage.s3 import uploader
from sqlalchemy.orm import Session
from app.core.logger_setup import logger, CentralizedLogger
from app.models.job import Job
from app.core.config import is_production
from app.database.session import get_db

logger = CentralizedLogger.get_logger(__name__)

async def upload_file(file: UploadFile,
        patient_id: str,
        priority: int,
        model_version: Optional[str],
        db: Session = Depends(get_db)):
    
    try:
        #Validator
        validator.validate_size(file)
        await validator.validate_pdf(file)

        # Compute Hash
        file_hash = validator.compute_hash(file)

        unique_key = uploader.get_s3_key(file.filename, patient_id)
        file_path = Path(f"files/{unique_key}")

        with open(file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
            
        # Job ORM object creation
        job = Job(
            patient_id=patient_id,
            input_type="pdf",
            file_url="object_url",
            original_filename=file.filename,
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

        if is_production():
            from app.worker.prod_tasks import schedule_prod_job

            schedule_prod_job(job.id, job.file_path)
            logger.info(f"Scheduled production pipeline for job {job_id_str}")
        else:
            from app.services.push_job_to_redis import push_job

            push_job(job.id, job.file_path)
            logger.info(f"Enqueued development pipeline for job {job_id_str}")

        return {"job_id": job.id, "job_status":job.status, "message":"Job Created Successfully"}

    except Exception as error:
        logger.error(f"Error Uploading file: {error}")
        db.rollback()
        raise
