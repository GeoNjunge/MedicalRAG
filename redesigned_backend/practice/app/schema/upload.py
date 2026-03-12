from fastapi import UploadFile, File, Form
from pydantic import Field
from typing import Optional
from pydantic import BaseModel

class UploadRequestSchema(BaseModel):
    file: UploadFile
    patient_id: str
    priority: int = Field(default=1, ge = 0, le = 10)
    model_version: Optional[str]

class UploadResponseSchema(BaseModel):
    job_id: str
    job_status: str
    message: str

