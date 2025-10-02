from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models.admin import Admin
from passlib.context import CryptContext
import hashlib

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/setup/create-tables")
def create_tables():
    """
    Create all database tables.
    This endpoint can be called to manually create tables if needed.
    """
    try:
        print("🔄 Creating database tables...")
        
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