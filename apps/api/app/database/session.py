from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool, StaticPool

from app.core.config import config


def normalize_database_url(database_url: str) -> str:
    """
    Normalize DATABASE_URL for synchronous SQLAlchemy usage.

    Accepts postgres/postgresql/postgresql+asyncpg URLs and maps them to the
    psycopg v3 driver used by the sync session layer.
    """
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace(
            "postgresql+asyncpg://", "postgresql+psycopg://", 1
        )
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def build_engine(database_url: str | None = None):
    url = normalize_database_url(database_url or config.DATABASE_URL)
    connect_args: dict = {}
    engine_kwargs: dict = {"pool_pre_ping": True}

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if url.endswith(":memory:") or url.rstrip("/").endswith(":memory:"):
            engine_kwargs["poolclass"] = StaticPool
        else:
            engine_kwargs["poolclass"] = NullPool
    elif url.startswith("postgresql"):
        engine_kwargs["poolclass"] = QueuePool
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10
        engine_kwargs["pool_recycle"] = 3600

    return create_engine(url, connect_args=connect_args, **engine_kwargs)


engine = build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
