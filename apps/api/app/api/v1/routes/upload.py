from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from app.schemas.upload import UploadResponseSchema
from typing import Optional
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.upload_services import upload_file
from app.core.logger_setup import CentralizedLogger
from app.core.auth import verify_api_key
from app.models.job import Job
from app.services.job_events import job_event_bus
import json
from fastapi.responses import StreamingResponse

logger = CentralizedLogger.get_logger(__name__)

router = APIRouter()


@router.post("/upload", response_model=UploadResponseSchema)
async def upload_medical_file(
    file: UploadFile = File(...),
    patient_id: str = Form(),
    priority: int = Form(1),
    model_version: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    try:
        result = await upload_file(
            file=file,
            patient_id=patient_id,
            priority=priority,
            model_version=model_version,
            db=db,
        )
        return result
    except Exception as e:
        logger.error(f"Upload API error: {e}")
        raise


async def _event_generator(job_id: str):
    async for payload in job_event_bus.subscribe(job_id):
        if payload.get("type") == "ping":
            yield ": ping\n\n"
            continue

        event_type = payload.get("type", "progress")
        yield f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"
        if event_type in {"completed", "failed"}:
            job_event_bus.clear(job_id)
            break


@router.get("/jobs/{job_id}/events")
async def stream_job_events(
    job_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    job = db.query(Job).filter(Job.id == str(job_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(
        _event_generator(job_id),
        media_type="text/event-stream",
        headers=headers,
    )
