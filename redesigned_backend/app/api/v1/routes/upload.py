from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.schemas.upload import UploadResponseSchema
from typing import Optional
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.upload_services import upload_file
from app.core.logger_setup import logger, CentralizedLogger
from app.worker.worker import redis_conn
from rq.job import Job

logger = CentralizedLogger.get_logger(__name__)

router = APIRouter()

@router.post("/upload", response_model=UploadResponseSchema)
async def upload_medical_file(
    file: UploadFile = File(...),
    patient_id: str = Form(),
    priority: int = Form(1),
    model_version: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        result = await upload_file(
            file=file,
            patient_id=patient_id,
            priority=priority,
            model_version=model_version,
            db=db
        )

        return result
    
    except Exception as e:
        logger.error(f"Upload API error: {e}")
        raise    


@router.get('/job_status/{job_id}')
def poll_job_status(job_id):
    try:
        job = Job.fetch(job_id, redis_conn)
        job_status = job.meta.get('status')

        return {
            "status": 200,
            "job_status": job_status,
        }

    except Exception as e:
        logger.error(f"Error getting job status {e}")
        return {
            "error": e
        }, 404