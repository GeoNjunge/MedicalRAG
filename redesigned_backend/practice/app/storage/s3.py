import boto3
from botocore import config
from practice.app.config.config import app_config
from practice.app.config.logger_setup import CentralizedLogger
from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

logger = CentralizedLogger.get_logger(__name__)

boto_config = config.Config(s3={"use_accelerate_endpoint": True})

s3_bucket_name = app_config.BUCKET_NAME
s3_bucket_region = app_config.REGION
s3_bucket_url = app_config.BUCKET_URL
s3_access_id = app_config.AWS_ACCESS_ID
s3_access_key = app_config.AWS_SECRET

s3_client = boto3.client(
    "s3",
    region_name = s3_bucket_region,
    aws_access_key_id = s3_access_id,
    aws_secret_access_key = s3_access_key,
    config = boto_config
)

class UploadService:
    @staticmethod
    async def get_key(file: UploadFile, patient_id: str):
        key = f"patients/{patient_id}/documents/{file.filename}"
        return key

    @staticmethod
    async def upload_to_s3(file: UploadFile, patient_id: str):
        try:
            key = await UploadService.get_key(file, patient_id)
            await run_in_threadpool(s3_client.upload_fileobj,
                                    file.file, 
                                    s3_bucket_name,
                                      key,
                                      ExtraArgs={'ContentType': file.content_type})

            logger.info(f"file{file.filename} has been uploaded by patient: {patient_id}")

            return {"object_url":f"https://aws.s3.{s3_bucket_name}/{key}", "filename":f"{file.filename}"}
        
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {e}")
            raise
        finally:
            file.file.close()

uploader = UploadService()