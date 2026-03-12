from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from app.core.config import config

database_url = config.DATABASE_URL

# set pre ping pool to true for serverless classes
engine = create_engine(
    database_url,
    pool_pre_ping=True
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
#         result = connection.execute(text("SELECT version();"))
#         for row in result:
#             print(row)

# except Exception as error:
#     print(f"Ërror connecting to the database: {error}")