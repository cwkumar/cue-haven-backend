import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Try to load .env file for local development only (Railway doesn't need this)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, that's fine for Railway

# Database URL - Railway will provide DATABASE_URL environment variable
DATABASE_URL = os.environ.get("DATABASE_URL") or os.getenv("DATABASE_URL")

# Debug: Print all environment info
print("=" * 70)
print("🔍 DATABASE CONFIGURATION DEBUG")
print("=" * 70)
print(f"DATABASE_URL environment variable: {'SET' if DATABASE_URL else 'NOT SET'}")

if DATABASE_URL:
    # Hide password for security
    safe_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
    print(f"✅ DATABASE_URL found in environment variables")
    print(f"📍 Connecting to: {safe_url}")
else:
    print("⚠️  WARNING: DATABASE_URL not found in environment!")
    print("⚠️  Using fallback localhost database (will fail on Railway)")
    print("\n🔧 TO FIX ON RAILWAY:")
    print("   1. Go to your backend service")
    print("   2. Click 'Variables' tab")
    print("   3. Add: DATABASE_URL=${{ Postgres.DATABASE_URL }}")
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/cuehaven"

# Railway provides DATABASE_URL in a format that needs to be updated for SQLAlchemy 2.0
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    print("🔄 Converting postgres:// to postgresql://")
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print("=" * 70)

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