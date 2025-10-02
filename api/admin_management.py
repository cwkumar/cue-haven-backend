from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.connection import get_db
from schemas.admin import AdminCreate, AdminUpdate, AdminResponse
from crud import admin as admin_crud
from api.admin import get_current_admin

router = APIRouter()

@router.get("/admins", response_model=List[AdminResponse])
def get_all_admins(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get all admins. Only accessible to authenticated admins."""
    if not current_admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can access admin list"
        )
    
    admins = admin_crud.get_all_admins(db, skip=skip, limit=limit)
    return admins

@router.post("/admins", response_model=AdminResponse)
def create_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create a new admin. Only accessible to superusers."""
    if not current_admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can create admins"
        )
    
    # Check if username already exists
    if admin_crud.get_admin_by_username(db, username=admin.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if admin_crud.get_admin_by_email(db, email=admin.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return admin_crud.create_admin(db=db, admin=admin)

@router.put("/admins/{admin_id}", response_model=AdminResponse)
def update_admin(
    admin_id: int,
    admin_update: AdminUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Update an admin. Only accessible to superusers or the admin themselves."""
    if not current_admin.is_superuser and current_admin.id != admin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this admin"
        )
    
    # If updating username, check if it's already taken
    if admin_update.username:
        existing_admin = admin_crud.get_admin_by_username(db, username=admin_update.username)
        if existing_admin and existing_admin.id != admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # If updating email, check if it's already taken
    if admin_update.email:
        existing_admin = admin_crud.get_admin_by_email(db, email=admin_update.email)
        if existing_admin and existing_admin.id != admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
    
    updated_admin = admin_crud.update_admin(db=db, admin_id=admin_id, admin_update=admin_update)
    if not updated_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    return updated_admin

@router.delete("/admins/{admin_id}")
def delete_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete (deactivate) an admin. Only accessible to superusers."""
    if not current_admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can delete admins"
        )
    
    # Prevent self-deletion
    if current_admin.id == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = admin_crud.delete_admin(db=db, admin_id=admin_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    return {"message": "Admin deleted successfully"}

@router.get("/admins/{admin_id}", response_model=AdminResponse)
def get_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get a specific admin by ID. Only accessible to superusers or the admin themselves."""
    if not current_admin.is_superuser and current_admin.id != admin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this admin"
        )
    
    admin = admin_crud.get_admin_by_id(db, admin_id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    return admin
