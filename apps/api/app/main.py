from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.routes.upload import router as upload_router
from app.core.logger_setup import CentralizedLogger
from fastapi.middleware.cors import CORSMiddleware
from app.database.init_db import init_db

# from app.database.init_db import init_db
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

logger = CentralizedLogger.get_logger(__name__)
app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:4200"
    "http://127.0.0.1:8000",
    "*"
]

app.add_middleware(CORSMiddleware, 
                   allow_origins=origins, 
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'])

app.include_router(upload_router, prefix="/api/v1")

@app.get("/")
def check_health():
    return {
        "name": __name__,
        "docs": "http://127.0.0.1:8000/docs",
        "status": "OK"
    }

if __name__ == "__main__":
    logger.info(f"Server running at http://127.0.0.1:8000")
    