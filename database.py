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

# Database URL - Build from Railway's individual environment variables
DATABASE_URL = None

# Method 1: Check if DATABASE_URL is already properly set
DATABASE_URL = os.environ.get("DATABASE_URL")

# Method 2: Validate DATABASE_URL and check for template variables
if DATABASE_URL:
    print(f"📋 Raw DATABASE_URL found: {DATABASE_URL[:50]}...")
    
    # Check for unresolved template variables or malformed URLs
    if ("${{" in DATABASE_URL or 
        not DATABASE_URL.startswith("postgresql://") or
        ":port/" in DATABASE_URL or
        "@host:" in DATABASE_URL):
        print("🔧 DATABASE_URL contains templates or is malformed, building from individual variables...")
        DATABASE_URL = None
    else:
        # Test if the URL is valid by trying to parse it
        try:
            from sqlalchemy.engine.url import make_url
            make_url(DATABASE_URL)  # This will raise an error if URL is invalid
            print("✅ DATABASE_URL validation passed")
        except Exception as e:
            print(f"⚠️  DATABASE_URL validation failed: {e}")
            DATABASE_URL = None

# Method 3: Build DATABASE_URL from Railway's individual environment variables
if not DATABASE_URL:
    postgres_user = os.environ.get("POSTGRES_USER")
    postgres_password = os.environ.get("POSTGRES_PASSWORD") 
    pghost = os.environ.get("PGHOST") or os.environ.get("RAILWAY_PRIVATE_DOMAIN")
    pgport = os.environ.get("PGPORT", "5432")
    postgres_db = os.environ.get("POSTGRES_DB") or os.environ.get("PGDATABASE", "railway")
    
    # Validate port is numeric
    try:
        port_num = int(pgport)
        if port_num <= 0 or port_num > 65535:
            raise ValueError(f"Invalid port number: {port_num}")
    except ValueError:
        print(f"⚠️  Invalid port '{pgport}', using default 5432")
        pgport = "5432"
    
    if all([postgres_user, postgres_password, pghost, postgres_db]):
        DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{pghost}:{pgport}/{postgres_db}"
        print(f"✅ Built DATABASE_URL from Railway environment variables")
        
        # Validate the constructed URL
        try:
            from sqlalchemy.engine.url import make_url
            make_url(DATABASE_URL)
        except Exception as e:
            print(f"❌ Constructed DATABASE_URL is invalid: {e}")
            DATABASE_URL = None
    else:
        print("❌ Missing Railway database environment variables")

# Debug: Print all environment info
print("=" * 70)
print("🔍 DATABASE CONFIGURATION DEBUG")
print("=" * 70)
print("📋 RAILWAY DATABASE VARIABLES:")
railway_db_vars = {
    "POSTGRES_USER": os.environ.get("POSTGRES_USER"),
    "POSTGRES_PASSWORD": "***" if os.environ.get("POSTGRES_PASSWORD") else "NOT SET",
    "POSTGRES_DB": os.environ.get("POSTGRES_DB"),
    "PGHOST": os.environ.get("PGHOST"),
    "RAILWAY_PRIVATE_DOMAIN": os.environ.get("RAILWAY_PRIVATE_DOMAIN"),
    "PGPORT": os.environ.get("PGPORT"),
    "DATABASE_URL": "SET" if DATABASE_URL else "NOT SET"
}

for key, value in railway_db_vars.items():
    print(f"   {key}: {value}")

print(f"\n🎯 Final DATABASE_URL: {'✅ READY' if DATABASE_URL else '❌ NOT SET'}")

if DATABASE_URL:
    # Hide password for security
    safe_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
    print(f"📍 Connecting to: {safe_url}")
else:
    print("❌ CRITICAL ERROR: Cannot build DATABASE_URL!")
    print("⚠️  Using fallback localhost database (WILL FAIL ON RAILWAY)")
    print("\n🔧 RAILWAY SETUP REQUIRED:")
    print("   1. Make sure PostgreSQL database is added to your Railway project")
    print("   2. Environment variables should be automatically available")
    print("   3. Check Railway dashboard for database connection info")
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/cuehaven"

# Railway provides DATABASE_URL in a format that needs to be updated for SQLAlchemy 2.0
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    print("🔄 Converting postgres:// to postgresql://")
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print("=" * 70)

# Create engine with error handling
try:
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        print("✅ Database engine created successfully")
    else:
        # Create a dummy engine that will allow the app to start but fail on actual DB operations
        print("⚠️  Creating fallback engine - database operations will fail until properly configured")
        engine = create_engine("postgresql://dummy:dummy@localhost:5432/dummy", strategy='mock', executor=lambda sql, *_: None)
        
except Exception as e:
    print(f"❌ Failed to create database engine: {e}")
    print("⚠️  Creating fallback engine - database operations will fail until properly configured")
    # Create a mock engine that allows the app to start
    from sqlalchemy import create_mock_engine
    
    def dump(sql, *multiparams, **params):
        print(f"🔧 Mock SQL execution: {sql}")
    
    engine = create_mock_engine('postgresql://', dump)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()