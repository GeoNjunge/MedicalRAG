from fastapi import UploadFile
from typing import Optional
from apps.api.app.services.file_validation import validator
from apps.api.app.storage.s3 import uploader
from sqlalchemy.orm import Session
from apps.api.app.core.logger_setup import logger, CentralizedLogger
from apps.api.app.models.job import Job
from apps.api.app.queue.job_queue import queue

logger = CentralizedLogger.get_logger(__name__)


def push_job(job_id, file_key):
    try:
        logger.info(f"--- ATTEMPTING REDIS ENQUEUE FOR {job_id} ---")
        # Use the string path to avoid import errors
        enqueued_job = queue.enqueue(
            "app.worker.tasks.process_ai_job", 
            args=(str(job_id), file_key),
            job_id=str(job_id)
        )
        logger.info(f"--- SUCCESS: Job {enqueued_job.id} is now in Redis ---")
        return enqueued_job
    except Exception as e:
        logger.error(f"!!! REDIS ENQUEUE FAILED: {e} !!!")
        raise