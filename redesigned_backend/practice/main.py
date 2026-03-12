from fastapi import FastAPI
from practice.app.routers.api.v1.upload_router import router as upload_router
from practice.app.config.logger_setup import CentralizedLogger, logger

logger = CentralizedLogger.get_logger(__name__)
app = FastAPI()

app.include_router(upload_router, prefix="/api/v1")

@app.get("/")
def check_health():
    return {
        "name": "Medical RAG",
        "status": "OK",
    }

if __name__ == "main":
    logger.info(f"Server is running on http://127.0.0.1:8000/")