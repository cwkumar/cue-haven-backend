from sqlalchemy.orm import Session
from models import Admin
from schemas import AdminCreate
import bcrypt

def get_admin_by_username(db: Session, username: str):
    return db.query(Admin).filter(Admin.username == username).first()

def get_admin_by_email(db: Session, email: str):
    return db.query(Admin).filter(Admin.email == email).first()

def create_admin(db: Session, admin: AdminCreate):
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

def authenticate_admin(db: Session, username: str, password: str):
    admin = get_admin_by_username(db, username)
    if not admin:
        return False
    if not admin.verify_password(password):
        return False
    return admin
