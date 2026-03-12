from app.database.base import Base
from app.database.session import engine
from app.models.job import Job
from app.core.logger_setup import logger, CentralizedLogger

logger = CentralizedLogger.get_logger(__name__)

def init_db():
    logger.info("Connecting to database to initialize tables...")
    try:
        # This will create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Confirmation check
        existing_tables = Base.metadata.tables.keys()
        logger.info(f"Successfully initialized! Tables detected: {list(existing_tables)}")
        
    except Exception as error:
        logger.error(f"Initialization failed: {error}")
        raise Exception(f"Initialization failed: {error}")

if __name__ == "__main__":
    init_db()
