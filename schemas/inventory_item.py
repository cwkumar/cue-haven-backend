from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class InventoryItemBase(BaseModel):
    item_name: str
    selling_price: float
    margin: float
    is_active: bool = True

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemUpdate(BaseModel):
    item_name: Optional[str] = None
    selling_price: Optional[float] = None
    margin: Optional[float] = None
    is_active: Optional[bool] = None

class InventoryItemResponse(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
