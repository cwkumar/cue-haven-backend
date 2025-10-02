from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, func
from models.table_session import TableSession, SessionItem
from models.inventory_item import InventoryItem
from schemas.table_session import TableSessionCreate, TableSessionUpdate, SessionItemCreate
from typing import List, Optional
from datetime import datetime, timezone

# Simplified rate structure: flat rates per table type regardless of people count
POOL_TABLE_RATE = 140.0  # Pool tables (Tables 1 & 2): ₹140/hour
MINI_SNOOKER_RATE = 180.0  # Mini Snooker table (Table 3): ₹180/hour

# Table configuration: Tables 1 & 2 are Pool, Table 3 is Mini Snooker
POOL_TABLES = [1, 2]
MINI_SNOOKER_TABLES = [3]

def get_table_type(table_number: int) -> str:
    """Get table type based on table number."""
    if table_number in POOL_TABLES:
        return "pool"
    elif table_number in MINI_SNOOKER_TABLES:
        return "mini_snooker"
    else:
        return "pool"  # Default to pool

def get_hourly_rate(table_number: int, number_of_people: int = None) -> float:
    """Get hourly rate based on table type only (simplified pricing)."""
    table_type = get_table_type(table_number)
    
    if table_type == "mini_snooker":
        return MINI_SNOOKER_RATE
    else:  # pool table
        return POOL_TABLE_RATE

def get_active_sessions(db: Session) -> List[TableSession]:
    """Get all active table sessions."""
    return (
        db.query(TableSession)
        .options(joinedload(TableSession.session_items).joinedload(SessionItem.inventory_item))
        .filter(TableSession.is_active == True)
        .order_by(TableSession.table_number)
        .all()
    )

def get_session_by_id(db: Session, session_id: int) -> Optional[TableSession]:
    """Get session by ID."""
    return (
        db.query(TableSession)
        .options(joinedload(TableSession.session_items).joinedload(SessionItem.inventory_item))
        .filter(TableSession.id == session_id)
        .first()
    )

def get_active_session_by_table(db: Session, table_number: int) -> Optional[TableSession]:
    """Get active session for a specific table."""
    return (
        db.query(TableSession)
        .options(joinedload(TableSession.session_items).joinedload(SessionItem.inventory_item))
        .filter(and_(TableSession.table_number == table_number, TableSession.is_active == True))
        .first()
    )

def create_table_session(db: Session, session: TableSessionCreate) -> TableSession:
    """Create a new table session."""
    # Check if table is already occupied
    existing_session = get_active_session_by_table(db, session.table_number)
    if existing_session:
        raise ValueError(f"Table {session.table_number} is already occupied")
    
    hourly_rate = get_hourly_rate(session.table_number, session.number_of_people)
    
    db_session = TableSession(
        table_number=session.table_number,
        customer_name=session.customer_name,
        number_of_people=session.number_of_people,
        hourly_rate=hourly_rate,
        notes=session.notes
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_table_session(db: Session, session_id: int, session_update: TableSessionUpdate) -> Optional[TableSession]:
    """Update a table session."""
    db_session = get_session_by_id(db, session_id)
    if not db_session or not db_session.is_active:
        return None
    
    update_data = session_update.dict(exclude_unset=True)
    
    # Update hourly rate if number of people changed
    if "number_of_people" in update_data:
        update_data["hourly_rate"] = get_hourly_rate(db_session.table_number, update_data["number_of_people"])
    
    for field, value in update_data.items():
        setattr(db_session, field, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session

def add_item_to_session(db: Session, session_id: int, item: SessionItemCreate) -> Optional[SessionItem]:
    """Add an item to a session."""
    db_session = get_session_by_id(db, session_id)
    if not db_session or not db_session.is_active:
        return None
    
    # Get inventory item
    inventory_item = db.query(InventoryItem).filter(
        and_(InventoryItem.id == item.inventory_item_id, InventoryItem.is_active == True)
    ).first()
    
    if not inventory_item:
        raise ValueError("Inventory item not found or inactive")
    
    # Check if item already exists in session
    existing_item = db.query(SessionItem).options(
        joinedload(SessionItem.inventory_item)
    ).filter(
        and_(
            SessionItem.session_id == session_id,
            SessionItem.inventory_item_id == item.inventory_item_id
        )
    ).first()
    
    if existing_item:
        # Update quantity and total price
        existing_item.quantity += item.quantity
        existing_item.total_price = existing_item.quantity * existing_item.unit_price
        db.commit()
        db.refresh(existing_item)
        
        # Update session items amount
        update_session_items_amount(db, session_id)
        return existing_item
    else:
        # Create new session item
        total_price = item.quantity * inventory_item.selling_price
        
        db_item = SessionItem(
            session_id=session_id,
            inventory_item_id=item.inventory_item_id,
            quantity=item.quantity,
            unit_price=inventory_item.selling_price,
            total_price=total_price
        )
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Load the item with its relationship
        db_item_with_inventory = db.query(SessionItem).options(
            joinedload(SessionItem.inventory_item)
        ).filter(SessionItem.id == db_item.id).first()
        
        # Update session items amount
        update_session_items_amount(db, session_id)
        return db_item_with_inventory

def remove_item_from_session(db: Session, session_id: int, item_id: int) -> bool:
    """Remove an item from a session."""
    db_item = db.query(SessionItem).filter(
        and_(SessionItem.id == item_id, SessionItem.session_id == session_id)
    ).first()
    
    if not db_item:
        return False
    
    db.delete(db_item)
    db.commit()
    
    # Update session items amount
    update_session_items_amount(db, session_id)
    return True

def update_session_items_amount(db: Session, session_id: int):
    """Update the total items amount for a session."""
    total_items_amount = db.query(SessionItem).filter(
        SessionItem.session_id == session_id
    ).with_entities(
        func.sum(SessionItem.total_price)
    ).scalar() or 0.0
    
    db_session = db.query(TableSession).filter(TableSession.id == session_id).first()
    if db_session:
        db_session.items_amount = total_items_amount
        db.commit()

def end_table_session(db: Session, session_id: int, end_time: Optional[datetime] = None) -> Optional[TableSession]:
    """End a table session and calculate total amount."""
    db_session = get_session_by_id(db, session_id)
    if not db_session or not db_session.is_active:
        return None
    
    # Set end time
    if end_time is None:
        end_time = datetime.now(timezone.utc)
    
    db_session.end_time = end_time
    db_session.is_active = False
    
    # Calculate time played in hours - handle timezone compatibility
    start_time = db_session.start_time
    
    # Ensure both datetimes have timezone info for calculation
    if start_time.tzinfo is None:
        # If start_time is naive, assume it's UTC
        start_time = start_time.replace(tzinfo=timezone.utc)
    
    if end_time.tzinfo is None:
        # If end_time is naive, assume it's UTC
        end_time = end_time.replace(tzinfo=timezone.utc)
    
    time_played = (end_time - start_time).total_seconds() / 3600
    
    # Calculate table charges
    table_charges = time_played * db_session.hourly_rate
    
    # Total amount = table charges + items amount
    db_session.total_amount = table_charges + db_session.items_amount
    
    db.commit()
    db.refresh(db_session)
    return db_session

def get_all_sessions(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[TableSession]:
    """Get all sessions with pagination."""
    query = db.query(TableSession).options(
        joinedload(TableSession.session_items).joinedload(SessionItem.inventory_item)
    )
    
    if active_only:
        query = query.filter(TableSession.is_active == True)
    
    return (
        query.order_by(desc(TableSession.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_old_session(db: Session, session: dict) -> TableSession:
    """Create a historical session with predefined start and end times."""
    from schemas.table_session import TableSessionOldCreate
    
    # Create the database session
    db_session = TableSession(
        table_number=session['table_number'],
        customer_name=session['customer_name'],
        number_of_people=session['number_of_people'],
        hourly_rate=session['hourly_rate'],
        start_time=session['start_time'],
        end_time=session['end_time'],
        total_amount=session['total_amount'],
        items_amount=session['items_amount'],
        is_active=session['is_active'],
        notes=session.get('notes', ''),
        created_at=session['start_time'],  # Set created_at to start_time for historical accuracy
        updated_at=session['end_time']     # Set updated_at to end_time
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session
