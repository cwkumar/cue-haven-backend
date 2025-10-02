import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database URL - Railway will provide DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL is provided, use a fallback for local development
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/cuehaven"

# Railway provides DATABASE_URL in a format that needs to be updated for SQLAlchemy 2.0
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()