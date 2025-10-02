from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.admin import Admin
from schemas.admin import AdminCreate, AdminUpdate
import bcrypt

def get_admin_by_username(db: Session, username: str):
    """Get admin by username."""
    return db.query(Admin).filter(Admin.username == username).first()

def get_admin_by_email(db: Session, email: str):
    """Get admin by email."""
    return db.query(Admin).filter(Admin.email == email).first()

def get_admin_by_id(db: Session, admin_id: int):
    """Get admin by ID."""
    return db.query(Admin).filter(Admin.id == admin_id).first()

def get_all_admins(db: Session, skip: int = 0, limit: int = 100):
    """Get all active admins with pagination."""
    return (
        db.query(Admin)
        .filter(Admin.is_active == True)
        .order_by(desc(Admin.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_admin(db: Session, admin: AdminCreate):
    """Create a new admin."""
    hashed_password = Admin.hash_password(admin.password)
    db_admin = Admin(
        username=admin.username,
        email=admin.email,
        full_name=admin.full_name,
        hashed_password=hashed_password,
        is_active=admin.is_active,
        is_superuser=admin.is_superuser
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def update_admin(db: Session, admin_id: int, admin_update: AdminUpdate):
    """Update an existing admin."""
    db_admin = get_admin_by_id(db, admin_id)
    if not db_admin:
        return None
    
    update_data = admin_update.dict(exclude_unset=True)
    
    # Hash password if provided
    if "password" in update_data:
        update_data["hashed_password"] = Admin.hash_password(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_admin, field, value)
    
    db.commit()
    db.refresh(db_admin)
    return db_admin

def delete_admin(db: Session, admin_id: int):
    """Soft delete an admin (set is_active to False)."""
    db_admin = get_admin_by_id(db, admin_id)
    if not db_admin:
        return False
    
    db_admin.is_active = False
    db.commit()
    return True

def authenticate_admin(db: Session, username: str, password: str):
    """Authenticate admin credentials."""
    admin = get_admin_by_username(db, username)
    if not admin:
        return False
    if not admin.verify_password(password):
        return False
    return admin
