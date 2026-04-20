from pydantic import BaseModel, Field
from fastapi import UploadFile
from typing import Optional
import json

class UploadRequestSchema(BaseModel):
    file: UploadFile
    patient_id: str
    priority: int = Field(default=1, ge = 0, le = 10)
    model_version: Optional[str]

class UploadResponseSchema(BaseModel):
    job_id: str
    job_status: str
    message: str
