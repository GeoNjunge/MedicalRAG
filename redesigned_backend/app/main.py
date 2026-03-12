from fastapi import FastAPI
from app.api.v1.routes.upload import router as upload_router
from app.core.logger_setup import logger, CentralizedLogger

logger = CentralizedLogger.get_logger(__name__)
app = FastAPI()

app.include_router(upload_router, prefix="/api/v1")

@app.get("/")
def check_health():
    return {
        "name": __name__,
        "status": "OK"
    }

if __name__ == "__main__":
    logger.info(f"Server running at http://127.0.0.1:8000")