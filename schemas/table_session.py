from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from .inventory_item import InventoryItemResponse

class SessionItemBase(BaseModel):
    inventory_item_id: int
    quantity: int = 1

class SessionItemCreate(SessionItemBase):
    pass

class SessionItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    inventory_item_id: int
    quantity: int
    unit_price: float
    total_price: float
    inventory_item: Optional[InventoryItemResponse] = None
    created_at: datetime

class TableSessionBase(BaseModel):
    table_number: int
    customer_name: str
    number_of_people: int
    notes: Optional[str] = None

class TableSessionCreate(TableSessionBase):
    pass

class TableSessionOldCreate(BaseModel):
    table_number: int
    customer_name: str
    number_of_people: int
    start_time: datetime
    end_time: datetime
    hourly_rate: float
    total_amount: float
    items_amount: float = 0
    is_active: bool = False
    notes: Optional[str] = None

class TableSessionUpdate(BaseModel):
    customer_name: Optional[str] = None
    number_of_people: Optional[int] = None
    notes: Optional[str] = None

class TableSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    table_number: int
    customer_name: str
    number_of_people: int
    hourly_rate: float
    start_time: datetime
    end_time: Optional[datetime] = None
    total_amount: float
    items_amount: float
    is_active: bool
    notes: Optional[str] = None
    session_items: List[SessionItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

class SessionEndRequest(BaseModel):
    end_time: Optional[datetime] = None

class SessionBillResponse(BaseModel):
    session: TableSessionResponse
    time_played_hours: float
    time_played_minutes: int
    table_charges: float
    items_charges: float
    total_amount: float
