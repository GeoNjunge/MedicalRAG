import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.session import get_db
from app.database.base import Base

# Setup a test database
SQL_ALCHEMY_DB_URL = "sqlite:///.test.db"
engine = create_engine(SQL_ALCHEMY_DB_URL, connect_args={"check_same_thread": False})
TestingLessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """
    Provides a clean database for each test
    """
    Base.metadata.create_all(bind=engine)
    session = TestingLessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
    

@pytest.fixture
def client(db_session):
    """Provides a TestClient with a DB dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    return TestClient(app)

@pytest.fixture
def mock_s3(mocker):
    return mocker.patch("app.storage.s3.s3_client_config")