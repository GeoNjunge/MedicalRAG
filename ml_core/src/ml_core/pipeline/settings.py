import os

from dotenv import load_dotenv

load_dotenv(dotenv_path="../../../../apps/api/.env")

PROD_BIOBERT_MODEL = "dmis-lab/biobert-v1.1"
PROD_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"


def get_app_env() -> str:
    return os.getenv("APP_ENV", "dev").strip().lower()


def is_production() -> bool:
    return get_app_env() in {"production", "prod"}


def configure_hf_hub_mode() -> None:
    if is_production():
        os.environ.pop("HF_HUB_OFFLINE", None)
    else:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
