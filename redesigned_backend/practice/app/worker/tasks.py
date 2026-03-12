from practice.app.config.logger_setup import logger, CentralizedLogger
from practice.app.models.job import Job
from datetime import datetime, timezone
from practice.app.worker.ai_pipeline.full_pipeline import run_ner_pipeline
from botocore.config import Config
from practice.app.database.init_db import Session
from practice.app.config.config import app_config
import boto3
from botocore.errorfactory import ClientError
import urllib.parse
from urllib.parse import urlparse

logger = CentralizedLogger.get_logger(__name__)

def retrieve_file_from_s3(obj_url):
    boto_config = Config(s3={"signature_version": "s3v4"})

    boto_s3_client = boto3.client(
        "s3",
        region_name=app_config.REGION,
        aws_access_key_id=app_config.AWS_ACCESS_ID,
        aws_secret_access_key=app_config.AWS_SECRET,
        config=boto_config
    )

    try:
        cleaned_url = urllib.parse.unquote(obj_url)

        parsed = urlparse(cleaned_url)

        key = parsed.path.lstrip('/')

        logger.info(f"Getting file from s3...")

        file = boto_s3_client.get_object(Bucket=app_config.BUCKET_NAME, Key=key)

        file_content = file['Body'].read()

        return file_content
    
    except ClientError as error:
        logger.error(f"Client failed to download: {error}")
        raise

    except Exception as e:
        logger.error(f"Error getting file from s3 bucket: {e}")
        raise


def process_ai_job(job_id):
     # Create new db session
    db = Session()
    try:
        logger.info("Started job processing...")
       
        # Retrieve the job from db
        job = db.query(Job).filter(Job.id == str(job_id)).first()

        if not job:
            raise Exception(f"Job does not exist")

        # Update status to processing
        job.status = "processing"
        job.started_at = datetime.now(timezone.utc)
        db.commit()
        
        # Download File from s3
        file = retrieve_file_from_s3(job.file_url)

        # run ner pipeline
        results = run_ner_pipeline(file)

        if "error" in results:
            job.error_message = results["error"]
            job.status = "failed"
            job.retry_count += 1
            db.commit()

        # Update fields
        job.extracted_text = results["extracted_text"]
        job.diseases_json = results["diseases_json"]
        job.labs_json = results["labs_json"]
        job.summary_text = results["summary_text"]
        job.completed_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Job : {job.id} has completed at {job.completed_at}")

        # If errors log them and raise them
    except Exception as e:
        logger.error(f"Error processing Job: {e}")
        if job:
            job.status = "failed"
            job.retry_count += 1

        db.commit()
        
        raise

    finally:
        db.close()

