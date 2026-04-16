from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.schemas.upload import UploadResponseSchema
from typing import Optional
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.upload_services import upload_file
from app.core.logger_setup import logger, CentralizedLogger
from app.worker.worker import redis_conn
from rq.job import Job
import random
import numpy as np

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

results =  {
        "diseases_json": [
          { "name":'Type 2 Diabetes Mellitus',      "icd10":'E11',    "confidence":0.97 },
          { "name":'Hypertension',                  "icd10":'I10',    "confidence":0.95 },
          { "name":'Chronic Kidney Disease Stage 3',"icd10":'N18.3',  "confidence":0.88 },
          { "name":'Peripheral Neuropathy',         "icd10":'G62.9',  "confidence":0.76 },
          { "name":'Hyperlipidemia',                "icd10":'E78.5',  "confidence":0.91 },
          { "name":'Diabetic Retinopathy',          "icd10":'E11.31', "confidence":0.69 },
        ],
        "labs_json": [
          { "test":'Fasting Glucose',  "value":'300', "unit":'mg/dL',          "reference":'70–100',  "status":'abnormal' },
          { "test":'HbA1c',            "value":'9.8', "unit":'%',               "reference":'<5.7',    "status":'abnormal' },
          { "test":'Creatinine',       "value":'2.1', "unit":'mg/dL',          "reference":'0.7–1.2', "status":'abnormal' },
          { "test":'eGFR',             "value":'38',  "unit":'mL/min/1.73m²',  "reference":'>60',     "status":'abnormal' },
          { "test":'LDL Cholesterol',  "value":'178', "unit":'mg/dL',          "reference":'<100',    "status":'abnormal' },
          { "test":'Hemoglobin',       "value":'12.4',"unit":'g/dL',           "reference":'12–17',   "status":'normal'   },
          { "test":'Sodium',           "value":'138', "unit":'mEq/L',          "reference":'136–145', "status":'normal'   },
          { "test":'Potassium',        "value":'4.2', "unit":'mEq/L',          "reference":'3.5–5.0', "status":'normal'   },
          { "test":'ALT',              "value":'42',  "unit":'U/L',             "reference":'7–56',    "status":'normal'   },
        ],
        "summary_text": 'The patient is a 58-year-old male presenting with poorly controlled Type 2 Diabetes Mellitus (HbA1c 9.8%) complicated by Chronic Kidney Disease Stage 3 (eGFR 38 mL/min/1.73m²) and peripheral neuropathy. Significant hyperglycemia is present with a fasting glucose of 300 mg/dL. Concurrent hypertension and hyperlipidemia (LDL 178 mg/dL) represent additional major cardiovascular risk factors. Evidence of early diabetic retinopathy was noted. Renal function indices suggest progressive nephropathy; urgent nephrology referral and RAAS inhibitor therapy optimization are warranted.',
            }

@router.get('/status/{job_id}')
def poll_job_status(job_id):
    # job_counter = -1

    try:
            job = Job.fetch(job_id, redis_conn)
            job_status = job.meta.get('status')
                  
        # if job_counter < len(job_status) - 1:
            # job_counter += 1
            if job_status['summary_text']: 
                  return {  
                            "diseases_json": job_status['diseases'],
                            "labs_json": job_status['lab_result'],
                            "summary_text": job_status['summary_text'],   
                        }
            return {
                # "status": 200,
                "status": job_status,
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
        
