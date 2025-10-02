from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from database import get_db
from models.admin import Admin
from schemas.admin import AdminCreate, AdminResponse, AdminLogin, Token
from crud.admin import (
    create_admin, 
    authenticate_admin, 
    get_admin_by_username, 
    get_admin_by_id,
    get_all_admins,
    update_admin,
    delete_admin
)
from auth import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Create separate routers
auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])
admin_router = APIRouter(prefix="/api/admin", tags=["Admin Management"])

# Security
security = HTTPBearer()

# Dependency to get current admin
def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    admin = get_admin_by_username(db, username=username)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return admin

# Authentication endpoints
@auth_router.post("/register", response_model=AdminResponse)
def register_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    """Register a new admin."""
    # Check if admin already exists
    if get_admin_by_username(db, admin.username):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    return create_admin(db=db, admin=admin)

@auth_router.post("/login", response_model=Token)
def login_admin(admin_login: AdminLogin, db: Session = Depends(get_db)):
    """Login admin and return access token."""
    admin = authenticate_admin(db, admin_login.username, admin_login.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me", response_model=AdminResponse)
def read_current_admin(current_admin: Admin = Depends(get_current_admin)):
    """Get current logged-in admin information."""
    return current_admin

# Admin management endpoints
@admin_router.get("/", response_model=List[AdminResponse])
def get_admins(skip: int = 0, limit: int = 100, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Get all admins (requires admin authentication)."""
    return get_all_admins(db, skip=skip, limit=limit)

@admin_router.get("/{admin_id}", response_model=AdminResponse)
def get_admin(admin_id: int, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Get specific admin by ID."""
    admin = get_admin_by_id(db, admin_id)
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

@admin_router.put("/{admin_id}", response_model=AdminResponse)
def update_admin_info(admin_id: int, admin_update: dict, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Update admin information."""
    admin = update_admin(db, admin_id, admin_update)
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

@admin_router.delete("/{admin_id}")
def delete_admin_account(admin_id: int, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Delete admin account."""
    admin = delete_admin(db, admin_id)
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return {"message": "Admin deleted successfully"}
