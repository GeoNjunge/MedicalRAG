from dotenv import load_dotenv
import os

load_dotenv()

class AppConfig():
    DATABASE_URL: str
    BUCKET_URL: str
    BUCKET_NAME: str
    REGION: str
    AWS_ACCESS_ID: str
    AWS_SECRET: str

AppConfig.AWS_ACCESS_ID = os.getenv("AWS_ACCESS_KEY")
AppConfig.DATABASE_URL = os.getenv("DATABASE_URL")
AppConfig.AWS_SECRET = os.getenv("AWS_SECRET_KEY")
AppConfig.REGION = os.getenv("S3_REGION_NAME")
AppConfig.BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AppConfig.BUCKET_URL = os.getenv("S3_BUCKET_URL")

app_config = AppConfig()