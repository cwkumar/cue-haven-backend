from sqlalchemy.orm import Session
from models.inventory_item import InventoryItem
from schemas.inventory_item import InventoryItemCreate, InventoryItemUpdate

def get_inventory_item_by_id(db: Session, item_id: int):
    """Get inventory item by ID."""
    return db.query(InventoryItem).filter(InventoryItem.id == item_id).first()

def get_inventory_item_by_name(db: Session, item_name: str):
    """Get inventory item by name."""
    return db.query(InventoryItem).filter(InventoryItem.item_name == item_name).first()

def get_all_inventory_items(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True):
    """Get all inventory items with pagination."""
    query = db.query(InventoryItem)
    if active_only:
        query = query.filter(InventoryItem.is_active == True)
    return query.offset(skip).limit(limit).all()

def create_inventory_item(db: Session, item: InventoryItemCreate):
    """Create a new inventory item."""
    db_item = InventoryItem(
        item_name=item.item_name,
        selling_price=item.selling_price,
        margin=item.margin,
        is_active=item.is_active
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_inventory_item(db: Session, item_id: int, item_update: InventoryItemUpdate):
    """Update an existing inventory item."""
    db_item = get_inventory_item_by_id(db, item_id)
    if db_item:
        update_data = item_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_inventory_item(db: Session, item_id: int):
    """Soft delete an inventory item by setting is_active to False."""
    db_item = get_inventory_item_by_id(db, item_id)
    if db_item:
        db_item.is_active = False
        db.commit()
        db.refresh(db_item)
    return db_item

def permanently_delete_inventory_item(db: Session, item_id: int):
    """Permanently delete an inventory item."""
    db_item = get_inventory_item_by_id(db, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item
