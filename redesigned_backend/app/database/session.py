from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from app.core.config import config

database_url = config.DATABASE_URL 
sqlite_file_name = "docs.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# set pre ping pool to true for serverless classes
engine = create_engine(
    sqlite_url,
    connect_args={'check_same_thread': False},
    pool_pre_ping=True,
    poolclass=StaticPool
)

# Create a configured session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# Connect and perform operations
# try:
#     with engine.connect() as connection:
#         print("Connection established with sql alchemy")

#         # Example using text for row execution
#         result = connection.execute(text("SELECT NAME FROM sqlite_master"))
#         for row in result:
#             print(row)

# except Exception as error:
#     print(f"Ërror connecting to the database: {error}")