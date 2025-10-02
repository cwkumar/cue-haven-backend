from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database.connection import get_db
from schemas.table_session import (
    TableSessionCreate, TableSessionUpdate, TableSessionResponse,
    SessionItemCreate, SessionItemResponse, SessionEndRequest, SessionBillResponse
)
from crud import table_session as session_crud
from api.admin import get_current_admin

router = APIRouter()

@router.get("/sessions/active", response_model=List[TableSessionResponse])
def get_active_sessions(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get all active table sessions."""
    sessions = session_crud.get_active_sessions(db)
    return sessions

@router.get("/sessions", response_model=List[TableSessionResponse])
def get_all_sessions(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get all sessions with pagination."""
    sessions = session_crud.get_all_sessions(db, skip=skip, limit=limit, active_only=active_only)
    return sessions

@router.get("/sessions/{session_id}", response_model=TableSessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Get a specific session by ID."""
    session = session_crud.get_session_by_id(db, session_id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session

@router.post("/sessions", response_model=TableSessionResponse)
def create_session(
    session: TableSessionCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create a new table session."""
    try:
        return session_crud.create_table_session(db=db, session=session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/sessions/{session_id}", response_model=TableSessionResponse)
def update_session(
    session_id: int,
    session_update: TableSessionUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Update a table session."""
    updated_session = session_crud.update_table_session(
        db=db, session_id=session_id, session_update=session_update
    )
    if not updated_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or not active"
        )
    return updated_session

@router.post("/sessions/{session_id}/items", response_model=SessionItemResponse)
def add_item_to_session(
    session_id: int,
    item: SessionItemCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Add an item to a session."""
    try:
        session_item = session_crud.add_item_to_session(db=db, session_id=session_id, item=item)
        if not session_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or not active"
            )
        return session_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/sessions/{session_id}/items/{item_id}")
def remove_item_from_session(
    session_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Remove an item from a session."""
    success = session_crud.remove_item_from_session(db=db, session_id=session_id, item_id=item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session item not found"
        )
    return {"message": "Item removed successfully"}

@router.post("/sessions/{session_id}/end", response_model=SessionBillResponse)
def end_session(
    session_id: int,
    end_request: SessionEndRequest = SessionEndRequest(),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """End a table session and calculate bill."""
    session = session_crud.end_table_session(
        db=db, session_id=session_id, end_time=end_request.end_time
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or already ended"
        )
    
    # Calculate bill details
    time_played_seconds = (session.end_time - session.start_time).total_seconds()
    time_played_hours = time_played_seconds / 3600
    time_played_minutes = int(time_played_seconds / 60)
    
    table_charges = time_played_hours * session.hourly_rate
    items_charges = session.items_amount
    total_amount = table_charges + items_charges
    
    bill_response = SessionBillResponse(
        session=session,
        time_played_hours=round(time_played_hours, 2),
        time_played_minutes=time_played_minutes,
        table_charges=round(table_charges, 2),
        items_charges=round(items_charges, 2),
        total_amount=round(total_amount, 2)
    )
    
    return bill_response

@router.get("/rates")
def get_hourly_rates(
    current_admin = Depends(get_current_admin)
):
    """Get simplified hourly rates by table type."""
    return {
        "pool_table_rate": 140.0,
        "mini_snooker_rate": 180.0,
        "table_types": {
            "1": "pool",
            "2": "pool", 
            "3": "mini_snooker"
        }
    }

@router.post("/sessions/old", response_model=TableSessionResponse)
def create_old_session(
    session_data: dict,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create a historical session with predefined start and end times."""
    try:
        old_session = session_crud.create_old_session(db=db, session=session_data)
        return old_session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create old session: {str(e)}"
        )
