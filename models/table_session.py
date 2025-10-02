from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base

class TableSession(Base):
    __tablename__ = "table_sessions"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer, nullable=False)
    customer_name = Column(String(100), nullable=False)
    number_of_people = Column(Integer, nullable=False)
    hourly_rate = Column(Float, nullable=False)  # Based on number of people
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    total_amount = Column(Float, default=0.0)
    items_amount = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to session items
    session_items = relationship("SessionItem", back_populates="session", cascade="all, delete-orphan")

class SessionItem(Base):
    __tablename__ = "session_items"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("table_sessions.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("TableSession", back_populates="session_items")
    inventory_item = relationship("InventoryItem")
