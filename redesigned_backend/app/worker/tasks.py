from app.core.logger_setup import logger, CentralizedLogger
from app.models.job import Job
from app.database.session import SessionLocal
from app.core.config import AppConfig 
from botocore.client import Config, ClientError
from app.worker.ai_pipeline import run_ner_pipeline
from urllib.parse import urlparse, unquote
from datetime import datetime, timezone

import boto3

app_config = AppConfig()
logger = CentralizedLogger.get_logger(__name__)

def read_from_s3_into_memory(input_str):
    """
    Download the image from the s3 bucket
    """
    # Configure to use aws accelerate
    boto_config = Config(s3={"use_accelerate_endpoint": True})

    # 1. If it's a full URL, extract just the path
    if input_str.startswith("http"):
        parsed = urlparse(input_str)
        # .path gives "/patients/123/..." - we strip the leading "/"
        key = parsed.path.lstrip('/')
    else:
        key = input_str

    # 2. IMPORTANT: Decode %20 and other characters back to spaces
    # S3 needs the literal key "LABORATORY TESTS", not "LABORATORY%20TESTS"
    actual_key = unquote(key)

    # 3. Strip bucket name if it's accidentally in the path 
    # (Common in ://s3.amazonaws.com URLs)
    bucket_name = app_config.S3_BUCKET_NAME
    if actual_key.startswith(f"{bucket_name}/"):
        actual_key = actual_key.replace(f"{bucket_name}/", "", 1)

    try:
        s3_client = boto3.client(
            "s3",
            region_name = app_config.S3_REGION_NAME,
            aws_access_key_id = app_config.AWS_ACCESS_KEY,
            aws_secret_access_key = app_config.AWS_SECRET_KEY,
            config = boto_config
        )


       
        response = s3_client.get_object(Bucket=bucket_name, Key = actual_key)

        # Read the content (body)
        file_content = response['Body'].read()

        return file_content
    
    except ClientError as error:
        logger.error(f"Client failed to download: {error}")
        raise
    
    except Exception as e:
        logger.error(f"Failed to download file: {e}")
        raise



def process_ai_job(job_id: str):
    """
    Background worker to process the job
    """
    job = None
    try:
        db = SessionLocal()

        logger.info(f"Processing job...")

        # Get job from db
        job = db.query(Job).filter(Job.id == str(job_id)).first()

        if not job:
            raise Exception("Job not found")
        
        # Change job status to processing
        job.started_at = datetime.now(timezone.utc)
        job.status = "processing"
        db.commit()

        # Download S3 image

        # Get s3
        obj_key = job.file_url

        file_content = read_from_s3_into_memory(obj_key)

        # Run AI pipeline -- later
        result = run_ner_pipeline(file_content) # dummy ner_pipeline

        if "error" in result:
            job.error_message = result["error"]
            job.status = "failed"
            # job.completed_at = datetime.now(timezone.utc)
            job.retry_count += 1
            db.commit()

        job.diseases_json = result["diseases_json"]
        job.extracted_text = result["extracted_text"]
        job.labs_json = result["labs_json"]
        job.summary_text = result["summary_text"]

        # Change job status to complete
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Job {job.id} completed at {job.completed_at}")

    except Exception as e:
        logger.error(f"Error occurred while processing AI job: {e}")
        if job:
            job.status = "failed"
            job.retry_count += 1
            
        db.commit()

        raise

    finally:
        db.close()