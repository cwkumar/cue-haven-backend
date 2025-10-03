from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from database import get_db, Base
from models.admin import Admin
from passlib.context import CryptContext
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_railway_engine():
    """
    Get SQLAlchemy engine with Railway database configuration.
    This rebuilds the connection each time to ensure fresh environment variables.
    """
    print("🔍 Getting Railway database engine...")
    
    # Method 1: Check if DATABASE_URL is properly set (not containing templates)
    database_url = os.environ.get("DATABASE_URL")
    print(f"📋 Raw DATABASE_URL: {database_url}")
    
    # Check if DATABASE_URL contains unresolved template variables
    if database_url and ("${{" in database_url or "port" in database_url.split(":")[-1]):
        print("⚠️  DATABASE_URL contains unresolved templates, ignoring...")
        database_url = None
    
    if database_url and database_url.startswith("postgresql://"):
        try:
            # Test if the URL is valid by trying to parse it
            from sqlalchemy.engine.url import make_url
            make_url(database_url)  # This will raise an error if URL is invalid
            print(f"✅ Using DATABASE_URL directly")
            return create_engine(database_url)
        except Exception as e:
            print(f"⚠️  DATABASE_URL is invalid: {e}")
            database_url = None
    
    # Method 2: Build DATABASE_URL from Railway's individual environment variables
    postgres_user = os.environ.get("POSTGRES_USER")
    postgres_password = os.environ.get("POSTGRES_PASSWORD") 
    pghost = os.environ.get("PGHOST") or os.environ.get("RAILWAY_PRIVATE_DOMAIN")
    pgport = os.environ.get("PGPORT", "5432")
    postgres_db = os.environ.get("POSTGRES_DB") or os.environ.get("PGDATABASE", "railway")
    
    print(f"🔍 Railway DB Connection Debug:")
    print(f"   POSTGRES_USER: {postgres_user or 'NOT SET'}")
    print(f"   POSTGRES_PASSWORD: {'***' if postgres_password else 'NOT SET'}")
    print(f"   PGHOST: {pghost or 'NOT SET'}")
    print(f"   RAILWAY_PRIVATE_DOMAIN: {os.environ.get('RAILWAY_PRIVATE_DOMAIN') or 'NOT SET'}")
    print(f"   PGPORT: {pgport}")
    print(f"   POSTGRES_DB: {postgres_db or 'NOT SET'}")
    
    # Validate port is numeric
    try:
        port_num = int(pgport)
        if port_num <= 0 or port_num > 65535:
            raise ValueError(f"Invalid port number: {port_num}")
    except ValueError as e:
        print(f"❌ Invalid port '{pgport}': {e}")
        pgport = "5432"  # Default PostgreSQL port
        print(f"🔄 Using default port: {pgport}")
    
    if all([postgres_user, postgres_password, pghost, postgres_db]):
        try:
            database_url = f"postgresql://{postgres_user}:{postgres_password}@{pghost}:{pgport}/{postgres_db}"
            print(f"✅ Built DATABASE_URL from individual variables")
            
            # Test the constructed URL
            from sqlalchemy.engine.url import make_url
            make_url(database_url)  # Validate URL format
            
            return create_engine(database_url)
        except Exception as e:
            print(f"❌ Error creating engine with built URL: {e}")
            raise Exception(f"Failed to create database engine: {e}")
    else:
        print("❌ Missing required Railway database environment variables")
        print("🔧 Available environment variables:")
        for key in sorted(os.environ.keys()):
            if any(term in key.upper() for term in ['DATABASE', 'POSTGRES', 'PG', 'RAILWAY']):
                value = os.environ[key]
                safe_value = value[:20] + "..." if len(value) > 20 else value
                print(f"     {key}: {safe_value}")
        
        # Provide specific guidance based on what's missing
        missing = []
        if not postgres_user:
            missing.append("POSTGRES_USER")
        if not postgres_password:
            missing.append("POSTGRES_PASSWORD")
        if not pghost:
            missing.append("PGHOST or RAILWAY_PRIVATE_DOMAIN")
        if not postgres_db:
            missing.append("POSTGRES_DB")
            
        raise Exception(f"Cannot build database connection - missing: {', '.join(missing)}. Railway database must be connected to your backend service.")
        
        # Fallback for local development (commented out for Railway)
        # return create_engine("postgresql://postgres:password@localhost:5432/cuehaven")

@router.get("/debug-env")
def debug_environment():
    """
    Debug endpoint to see all available environment variables.
    This helps troubleshoot Railway database connection issues.
    """
    env_vars = {}
    
    # Collect all environment variables that might be related to database
    for key, value in os.environ.items():
        if any(term in key.upper() for term in ['DATABASE', 'POSTGRES', 'PG', 'DB', 'RAILWAY']):
            # Hide sensitive data but show structure
            if 'PASSWORD' in key.upper():
                safe_value = value[:3] + "***" + value[-3:] if len(value) > 6 else "***"
            else:
                safe_value = value
            env_vars[key] = safe_value
    
    # Check specific variables we need
    db_vars = {
        "POSTGRES_USER": os.environ.get("POSTGRES_USER"),
        "POSTGRES_PASSWORD": "***" if os.environ.get("POSTGRES_PASSWORD") else None,
        "POSTGRES_DB": os.environ.get("POSTGRES_DB"),
        "PGHOST": os.environ.get("PGHOST"),
        "RAILWAY_PRIVATE_DOMAIN": os.environ.get("RAILWAY_PRIVATE_DOMAIN"),
        "PGPORT": os.environ.get("PGPORT"),
        "DATABASE_URL": "SET" if os.environ.get("DATABASE_URL") else None
    }
    
    return {
        "all_db_related_vars": env_vars,
        "required_variables": db_vars,
        "can_build_url": all([
            os.environ.get("POSTGRES_USER"),
            os.environ.get("POSTGRES_PASSWORD"), 
            os.environ.get("PGHOST") or os.environ.get("RAILWAY_PRIVATE_DOMAIN"),
            os.environ.get("POSTGRES_DB")
        ])
    }

@router.post("/create-tables")
def create_tables():
    """
    Create all database tables.
    This endpoint can be called to manually create tables if needed.
    """
    try:
        print("🔄 Creating database tables...")
        
        # Get Railway engine with fresh environment variables
        engine = get_railway_engine()
        
        # Import all models to ensure they are registered with Base
        from models import admin, table_session, inventory_item
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        return {
            "success": True,
            "message": "Database tables created successfully"
        }
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating tables: {str(e)}")

@router.post("/setup/create-admin")
def create_default_admin(db: Session = Depends(get_db)):
    """
    Create a default admin user if one doesn't exist.
    Default credentials: admin / cuehaven2024
    """
    try:
        # Check if admin already exists
        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()
        if existing_admin:
            return {
                "success": True,
                "message": "Admin user already exists",
                "username": "admin"
            }
        
        # Create default admin
        default_password = "cuehaven2024"
        hashed_password = pwd_context.hash(default_password)
        
        admin_user = Admin(
            username="admin",
            password_hash=hashed_password
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Default admin user created successfully!")
        return {
            "success": True,
            "message": "Default admin user created successfully",
            "username": "admin",
            "password": default_password,
            "note": "Please change the password after first login"
        }
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating admin: {str(e)}")

@router.post("/setup/full-setup")
def full_setup(db: Session = Depends(get_db)):
    """
    Complete setup: Create tables and default admin user.
    This is a one-click setup for Railway deployment.
    """
    try:
        # Step 1: Create tables
        print("🔄 Step 1: Creating database tables...")
        
        # Get Railway engine with fresh environment variables
        engine = get_railway_engine()
        
        from models import admin, table_session, inventory_item
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created!")
        
        # Step 2: Create admin user
        print("🔄 Step 2: Creating default admin...")
        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()
        
        if not existing_admin:
            default_password = "cuehaven2024"
            hashed_password = pwd_context.hash(default_password)
            
            admin_user = Admin(
                username="admin",
                password_hash=hashed_password
            )
            
            db.add(admin_user)
            db.commit()
            admin_created = True
        else:
            admin_created = False
        
        print("✅ Full setup completed!")
        return {
            "success": True,
            "message": "Full setup completed successfully",
            "tables_created": True,
            "admin_created": admin_created,
            "admin_credentials": {
                "username": "admin",
                "password": "cuehaven2024" if admin_created else "Already exists"
            },
            "note": "Please change the admin password after first login"
        }
    except Exception as e:
        db.rollback()
        print(f"❌ Error in full setup: {e}")
        raise HTTPException(status_code=500, detail=f"Error in full setup: {str(e)}")

@router.get("/setup/status")
def setup_status(db: Session = Depends(get_db)):
    """
    Check the current setup status of the database.
    """
    try:
        # Check if tables exist by trying to query admin table
        try:
            admin_count = db.query(Admin).count()
            tables_exist = True
        except:
            tables_exist = False
            admin_count = 0
        
        return {
            "database_connected": True,
            "tables_exist": tables_exist,
            "admin_users_count": admin_count,
            "admin_exists": admin_count > 0,
            "ready_for_use": tables_exist and admin_count > 0
        }
    except Exception as e:
        return {
            "database_connected": False,
            "error": str(e),
            "tables_exist": False,
            "admin_users_count": 0,
            "admin_exists": False,
            "ready_for_use": False
        }