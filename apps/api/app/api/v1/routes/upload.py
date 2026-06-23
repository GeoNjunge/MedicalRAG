from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.schemas.upload import UploadResponseSchema
from typing import Optional
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.upload_services import upload_file
from app.core.logger_setup import logger, CentralizedLogger
from app.worker.worker import redis_conn
from app.models.job import Job
import random
import numpy as np
import rq

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

job_status = [
    'Extracting document text...',
    'Running NLP tokenization...',
    'Extracting named entities...',
    'Identifying lab values...',
    'Mapping to ICD-10 codes...',
    'Generating clinical summary...',
]


db: Session = Depends(get_db)
@router.get('/status/{job_id}')
def poll_job_status(job_id):
    # job_counter = -1

    try:
            job = rq.job.Job.fetch(job_id, redis_conn)

            if job is not None:
                job_status = job.meta.get('status')
                    
                if 'summary_text' in job_status: 
                    return {  
                                "status": "Completed",
                                "diseases_json": job_status['diseases_json'],
                                "labs_json": job_status['labs_json'],
                                "summary_text": job_status['summary_text'],   
                            }
                
            job = db.query(Job).filter(Job.id == str(job_id)).first()
            if job is not None:
                return {  
                                    "status": job.status,
                                    "diseases_json": job.diseases_json,
                                    "labs_json": job.labs_json,
                                    "summary_text": job.summary_text,   
                                }
                # else:
            return {
                # "status": 200,
               "status": str(job_status),
            }
    # 
        # return results

    except Exception as e:
                logger.error(f"Error getting job status {e}")
                return {
                    "error": e
                }, 404
    
sample_res =  {
    "diseases_json": [
        "chest pain",
        "GERD",
        "heart problems",
        "HTN",
        "hypertension",
        "TAH",
        "premature",
        "CAD",
        "uterine fibroids",
        "peptic ulcer disease",
        "rash",
        "hives",
        "headache",
        "heart attack",
        "Epigastric pain",
        "lower back pain",
        "Chest Pain Dyspnea",
        "allergy",
        "ASCVD",
        "dyspnea",
        "Lumbosacral back pain",
        "angina pectoris",
        "substernal chest pain",
        "ischemic cardiac",
        "coronary artery disease",
        "unstable angina",
        "Gastro-esophageal reflux disease",
        "ischemic heart disease",
        "left ventricular dysfunction",
        "congestive heart failure",
        "myocardial ischemia",
        "abdominal bruit",
        "ASCVD of the renal artery",
        "renovascular hypertension",
        "valvular heart disease",
        "aortic stenosis",
        "Epigastric discomfort",
        "Lumbo-sacral back pain",
        "Fibrocystic breast disease",
        "Penicillin allergy",
        "esophageal reflux disease",
        "pulmonary or musculoskeletal pain",
        "myocardial infarction",
        "volume overload",
        "wall motion abnormalities"
    ],
    "labs_json": [
        {
            "test": "BUN",
            "value": "N/A",
            "unit": "",
            "status": "NORMAL"
        },
        {
            "test": "CREATININE",
            "value": "N/A",
            "unit": "",
            "status": "NORMAL"
        }
    ],
    "summary_text": "The patient has cancer with a glucose level of 300 mg/l"
}
        
