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
    APP_ENV: str = "dev"
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:4200"
    CORS_ORIGINS: Optional[str] = None
    DATABASE_URL:str
    S3_BUCKET_URL: str
    S3_BUCKET_NAME: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    S3_REGION_NAME :str
    OLLAMA_URL: str
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: Optional[str] = None

    model_config = SettingsConfigDict(
          env_file='.env',
          env_file_encoding="utf-8",
          case_sensitive=False
    )


config = AppConfig()


def is_production() -> bool:
    return config.APP_ENV.strip().lower() in {"production", "prod"}


def get_cors_origins() -> list[str]:
    if config.CORS_ORIGINS:
        return [origin.strip() for origin in config.CORS_ORIGINS.split(",") if origin.strip()]

    origins = {config.FRONTEND_URL.rstrip("/")}
    if not is_production():
        origins.update(
            {
                "http://localhost:4200",
                "http://127.0.0.1:4200",
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                "https://medical-rag-dli1-rose.vercel.app/"
            }
        )
    return sorted(origins)


if not config.DATABASE_URL:
        logger.error('Cannot read DATABASE URL')
        raise RuntimeError('Cannot read DATABASE URL')

