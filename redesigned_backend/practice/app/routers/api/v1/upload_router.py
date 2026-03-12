from fastapi import APIRouter, File, Form, HTTPException
from practice.app.schema.upload import UploadResponseSchema
from fastapi import UploadFile, Depends
from practice.app.services.upload_service import upload_service
from practice.app.config.logger_setup import CentralizedLogger
from sqlalchemy.orm import Session
from practice.app.database.init_db import get_db

logger = CentralizedLogger.get_logger(__name__)
router = APIRouter()

@router.post("/upload", response_model=UploadResponseSchema)
async def uploader_function(
        file: UploadFile = File(...),
        patient_id: str = Form(...),
        priority: int = Form(...), 
        model_version: str = Form(...),
        db: Session = Depends(get_db)
):
    try:
        result = await upload_service(file, patient_id, priority, model_version, db)

        return {
            "job_id": result["job_id"],
            "job_status": result["job_status"],
            "message":"Success"
        }
    except Exception as e:
        logger.error(f"Failed to upload; {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
