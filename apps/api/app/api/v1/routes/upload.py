from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.schemas.upload import UploadResponseSchema
from typing import Optional
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.upload_services import upload_file
from app.core.logger_setup import logger, CentralizedLogger
from app.worker.worker import redis_conn
import json
import asyncio
import rq
from fastapi.responses import StreamingResponse

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
        # return {
            # "job_id": "job-0001", "job_status":"Pending", "message":"Job Created Successfully"
        # }
    
    except Exception as e:
        logger.error(f"Upload API error: {e}")
        raise    

@router.get("/jobs/{job_id}/events")
async def stream_job_events(job_id: str):
    async def event_generator():
        try:
            job = rq.job.Job.fetch(job_id, redis_conn)
            initial_status = job.meta.get("status")
            if initial_status:
                if isinstance(initial_status, dict):
                    initial_event = {
                        "type": "completed",
                        "job_id": str(job_id),
                        "stage": "completed",
                        "status": "Completed",
                        "result": initial_status,
                    }
                    yield f"event: completed\ndata: {json.dumps(initial_event)}\n\n"
                    return
                initial_event = {
                    "type": "progress",
                    "job_id": str(job_id),
                    "stage": "processing",
                    "status": str(initial_status),
                }
                yield f"event: progress\ndata: {json.dumps(initial_event)}\n\n"
        except Exception:
            # Job may not exist yet; continue waiting for pubsub events.
            pass

        pubsub = redis_conn.pubsub()
        channel = f"job_events:{job_id}"
        pubsub.subscribe(channel)

        try:
            while True:
                message = pubsub.get_message(ignore_subscribe_messages=True)

                if message and message.get("type") == "message":
                    raw_data = message.get("data")
                    if isinstance(raw_data, bytes):
                        raw_data = raw_data.decode("utf-8")

                    payload = json.loads(raw_data)
                    event_type = payload.get("type", "progress")
                    yield f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"

                    if event_type in {"completed", "failed"}:
                        break
                else:
                    # Keep connection alive through proxies/load balancers.
                    yield ": ping\n\n"
                    await asyncio.sleep(1.0)
        finally:
            pubsub.unsubscribe(channel)
            pubsub.close()

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers=headers,
    )
