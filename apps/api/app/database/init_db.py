from sqlalchemy import inspect, text

from app.database.base import Base
from app.database.session import engine
from app.models.job import Job
from app.core.logger_setup import logger, CentralizedLogger

logger = CentralizedLogger.get_logger(__name__)

def init_db():
    logger.info("Connecting to database to initialize tables...")
    try:
        # This will create tables if they don't exist
        Base.metadata.create_all(
            bind=engine
        )
        _ensure_token_metrics_column()

        # Confirmation check
        existing_tables = Base.metadata.tables.keys()
        logger.info(f"Successfully initialized! Tables detected: {list(existing_tables)}")
        
    except Exception as error:
        logger.error(f"Initialization failed: {error}")
        raise Exception(f"Initialization failed: {error}")


def _ensure_token_metrics_column() -> None:
    """Add token_metrics_json to existing SQLite databases created before this column."""
    inspector = inspect(engine)
    if "jobs" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("jobs")}
    if "token_metrics_json" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE jobs ADD COLUMN token_metrics_json JSON"))
    logger.info("Added jobs.token_metrics_json column")

if __name__ == "__main__":
    init_db()
