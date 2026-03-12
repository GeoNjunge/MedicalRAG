import uuid
import boto3
from app.core.config import config as app_config
from fastapi import UploadFile
from botocore.client import Config
from app.core.logger_setup import CentralizedLogger
from starlette.concurrency import run_in_threadpool

logger = CentralizedLogger.get_logger(__name__)

# Configure to use aws accelerate
boto_config = Config(s3={"use_accelerate_endpoint": True})

try:
    s3_client_config = boto3.client(
        "s3",
        region_name = app_config.S3_REGION_NAME,
        aws_access_key_id = app_config.AWS_ACCESS_KEY,
        aws_secret_access_key = app_config.AWS_SECRET_KEY,
        config = boto_config
    )

except ValueError as error:
    logger.error("Error creating client: {e}")


class Uploader():
    @staticmethod
    async def get_s3_key(filename, patient_id):
        try:
            new_id = uuid.uuid4()
            key = f"patients/{patient_id}/jobs/{new_id}_{filename}"
            return key
        except RuntimeError as e:
            logger.error(f"Error getting s3 key: {e}")
            raise RuntimeError(f"Could not generate signed key{e}")
            
    @staticmethod        
    async def upload_file_to_s3(file: UploadFile, patient_id):
        key = await Uploader.get_s3_key(file.filename, patient_id)
        S3_BUCKET_NAME = app_config.S3_BUCKET_NAME
        s3_client = s3_client_config

        try:
            await run_in_threadpool(s3_client.upload_fileobj,
                                    file.file,
                                    S3_BUCKET_NAME,
                                    key,
                                    ExtraArgs={'ContentType': file.content_type})
            
            logger.info(f"Uploading file{file.filename}...")

            # presigned_url = await s3_client.generate_presigned_url(
            #     'get_object',
            #     Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
            #     ExpiresIn=3600
            # ) # incase we need limited access to file

            object_url = f"https://{S3_BUCKET_NAME}.s3.{app_config.S3_REGION_NAME}://{key}"

            return {"filename": file.filename, "key": key, "object_url": object_url, "message": "Upload successful"}
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}")
            raise RuntimeError(f"Error uploading file to s3: {e}")
        finally:
            await file.close()

uploader = Uploader()