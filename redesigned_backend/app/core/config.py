from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from app.core.logger_setup import logger, CentralizedLogger
import os

logger = CentralizedLogger.get_logger(__name__)

load_dotenv()

class AppConfig(BaseSettings):
    """"
    Configuration class for the application. Loaded from .env
    """
    DATABASE_URL:str
    S3_BUCKET_URL: str
    S3_BUCKET_NAME: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    S3_REGION_NAME :str

    model_config = SettingsConfigDict(
          env_file='.env',
          env_file_encoding="utf-8",
          case_sensitive=False
    )


    

config = AppConfig()

if not config.DATABASE_URL:
        logger.error('Cannot read DATABASE URL')
        raise RuntimeError('Cannot read DATABASE URL')

