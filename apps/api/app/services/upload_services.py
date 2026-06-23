from pathlib import Path

from fastapi import Depends, UploadFile
from typing import Optional
from app.services.file_validation import validator
from app.storage.s3 import uploader
from sqlalchemy.orm import Session
from app.core.logger_setup import logger, CentralizedLogger
from app.models.job import Job
from app.queue.job_queue import queue
from app.services.push_job_to_redis import push_job
from app.worker.ai_pipeline import update_status
from app.database.session import get_db
import rq

from app.worker.worker import redis_conn

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

        # check if file hash exists in any job
        # hash_exists = db.query(Job).filter(Job.file_hash == str(file_hash)).first()

        # if hash_exists:
        #     result = {
        #         "extracted_text": hash_exists.extracted_text,
        #         "diseases_json": hash_exists.diseases_json,
        #         "labs_json": hash_exists.labs_json,
        #         "summary_text": hash_exists.summary_text,
        #     }

        #     job = rq.job.Job.fetch(hash_exists.id, redis_conn)

        #     if job is None:
        #         update_status(result, job)

        #     return {"job_id": hash_exists.id, "job_status":"Complete", "message":"Job already completed"}
        # Upload to S3
        # result = await uploader.upload_file_to_s3(file, patient_id)

        # Well change this to be save job to in memory 
        # Well also need key for uniqueness
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
        # 1. Store the ID as a plain string immediately
        # This avoids issues if refresh() hangs
        job_id_str = str(job.id)
        
        try:
            db.refresh(job)
            logger.info(f"Job refreshed. ID: {job_id_str}")
        except Exception as e:
            logger.warning(f"Refresh failed but continuing: {e}")
        # Push job_id to queue
        push_job(job.id, job.file_path)

        # Return 
        return {"job_id": job.id, "job_status":job.status, "message":"Job Created Successfully"}

    except Exception as error:
        logger.error(f"Error Uploading file: {error}")
        db.rollback()
        raise