from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Request
from app.schemas.upload import UploadResponseSchema
from typing import Optional
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.upload_services import upload_file
from app.core.logger_setup import CentralizedLogger
from app.core.auth import verify_api_key
from app.core.audit_logger import (
    log_job_status_fetched,
    log_sse_connected,
    log_upload_created,
)
from app.models.job import Job
from app.services.job_events import job_event_bus
import json
from fastapi.responses import StreamingResponse

logger = CentralizedLogger.get_logger(__name__)

router = APIRouter()


@router.post("/upload", response_model=UploadResponseSchema)
async def upload_medical_file(
    request: Request,
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
        log_upload_created(
            request,
            job_id=str(result["job_id"]),
            patient_id=patient_id,
            status=str(result["job_status"]),
        )
        return result
    except Exception as e:
        logger.error(f"Upload API error: {e}")
        raise


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    job = db.query(Job).filter(Job.id == str(job_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    log_job_status_fetched(request, job_id=str(job.id), status=job.status)
    return {
        "job_id": job.id,
        "status": job.status,
        "patient_id": job.patient_id,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
    }


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
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    job = db.query(Job).filter(Job.id == str(job_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    log_sse_connected(request, job_id=str(job.id), status=job.status)

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
