from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import config

database_url = config.DATABASE_URL
connect_args: dict = {}
poolclass = None

if database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    poolclass = StaticPool

engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    poolclass=poolclass,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
