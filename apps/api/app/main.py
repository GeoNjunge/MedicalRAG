from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from app.api.v1.routes.upload import router as upload_router
from app.core.logger_setup import CentralizedLogger
from fastapi.middleware.cors import CORSMiddleware
from app.database.init_db import init_db
from app.core.config import config, get_cors_origins, is_production
from ml_core.pipeline.resources import initialize_pipeline_resources, initialize_prod_resources

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if is_production():
        resources = await asyncio.to_thread(initialize_prod_resources)
    else:
        resources = await asyncio.to_thread(initialize_pipeline_resources)
    app.state.pipeline_resources = resources
    yield

logger = CentralizedLogger.get_logger(__name__)
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api/v1")

@app.get("/")
def check_health():
    backend_url = config.BACKEND_URL.rstrip("/")
    return {
        "name": __name__,
        "docs": f"{backend_url}/docs",
        "frontend_url": config.FRONTEND_URL,
        "status": "OK",
    }

if __name__ == "__main__":
    logger.info(f"Server running at {config.BACKEND_URL.rstrip('/')}")
