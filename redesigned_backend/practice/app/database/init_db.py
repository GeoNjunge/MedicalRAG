from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from practice.app.config.config import app_config
from practice.app.config.logger_setup import logger, CentralizedLogger
from practice.app.database.base import Base

DATABASE_URL = app_config.DATABASE_URL

engine = create_engine(DATABASE_URL,
                   pool_pre_ping=True
                   )

Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
db = Session()

def get_db():
    try:
        yield db
    finally:
        db.close()