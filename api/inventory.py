from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.admin import Admin
from schemas.inventory_item import InventoryItemCreate, InventoryItemResponse, InventoryItemUpdate
from crud.inventory_item import (
    create_inventory_item,
    get_inventory_item_by_id,
    get_inventory_item_by_name,
    get_all_inventory_items,
    update_inventory_item,
    delete_inventory_item,
    permanently_delete_inventory_item
)
from auth import verify_token
from crud.admin import get_admin_by_username

router = APIRouter(prefix="/api/inventory", tags=["Inventory Management"])

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

# Inventory item endpoints
@router.get("/items", response_model=List[InventoryItemResponse])
def get_inventory_items(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = True,
    current_admin: Admin = Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    """Get all inventory items."""
    return get_all_inventory_items(db, skip=skip, limit=limit, active_only=active_only)

@router.get("/items/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(
    item_id: int, 
    current_admin: Admin = Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    """Get specific inventory item by ID."""
    item = get_inventory_item_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item

@router.post("/items", response_model=InventoryItemResponse)
def create_new_inventory_item(
    item: InventoryItemCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new inventory item."""
    # Check if item with same name already exists
    existing_item = get_inventory_item_by_name(db, item.item_name)
    if existing_item:
        raise HTTPException(
            status_code=400,
            detail="Item with this name already exists"
        )
    return create_inventory_item(db=db, item=item)

@router.put("/items/{item_id}", response_model=InventoryItemResponse)
def update_inventory_item_endpoint(
    item_id: int,
    item_update: InventoryItemUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update inventory item."""
    item = update_inventory_item(db, item_id, item_update)
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item

@router.delete("/items/{item_id}")
def delete_inventory_item_endpoint(
    item_id: int,
    permanent: bool = False,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete inventory item (soft delete by default, permanent if specified)."""
    if permanent:
        item = permanently_delete_inventory_item(db, item_id)
    else:
        item = delete_inventory_item(db, item_id)
    
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    return {"message": f"Inventory item {'permanently deleted' if permanent else 'deactivated'} successfully"}
