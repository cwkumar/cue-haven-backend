from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn

# Import our modules
from database import SessionLocal, engine, Base
from api.admin import auth_router, admin_router
from api.inventory import router as inventory_router
from api.admin_management import router as admin_management_router
from api.table_sessions import router as table_sessions_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cue Haven API",
    description="API for the Cue Haven Billiards Club",
    version="1.0.0"
)

# CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000", "http://127.0.0.1:5173", "http://0.0.0.0:5173"],  # SvelteKit dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(inventory_router)
app.include_router(admin_management_router, prefix="/api/admin-management", tags=["admin-management"])
app.include_router(table_sessions_router, prefix="/api/table-sessions", tags=["table-sessions"])

# Pydantic models for other features
class TableBooking(BaseModel):
    id: Optional[int] = None
    customer_name: str
    customer_email: str
    table_number: int
    booking_date: datetime
    duration_hours: int
    status: str = "confirmed"

class Tournament(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    entry_fee: float
    max_participants: int
    tournament_date: datetime
    status: str = "upcoming"

# In-memory storage (replace with database in production)
bookings: List[TableBooking] = []
tournaments: List[Tournament] = []

@app.get("/")
def read_root():
    return {"message": "Welcome to Cue Haven API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Table booking endpoints
@app.get("/api/bookings", response_model=List[TableBooking])
def get_bookings():
    return bookings

@app.post("/api/bookings", response_model=TableBooking)
def create_booking(booking: TableBooking):
    booking.id = len(bookings) + 1
    bookings.append(booking)
    return booking

@app.get("/api/bookings/{booking_id}", response_model=TableBooking)
def get_booking(booking_id: int):
    for booking in bookings:
        if booking.id == booking_id:
            return booking
    raise HTTPException(status_code=404, detail="Booking not found")

# Tournament endpoints
@app.get("/api/tournaments", response_model=List[Tournament])
def get_tournaments():
    return tournaments

@app.post("/api/tournaments", response_model=Tournament)
def create_tournament(tournament: Tournament):
    tournament.id = len(tournaments) + 1
    tournaments.append(tournament)
    return tournament

@app.get("/api/tournaments/{tournament_id}", response_model=Tournament)
def get_tournament(tournament_id: int):
    for tournament in tournaments:
        if tournament.id == tournament_id:
            return tournament
    raise HTTPException(status_code=404, detail="Tournament not found")

# Tables endpoint
@app.get("/api/tables")
def get_available_tables():
    # Mock data for available tables
    tables = [
        {"id": 1, "name": "Table 1", "type": "8-Ball", "status": "available"},
        {"id": 2, "name": "Table 2", "type": "9-Ball", "status": "occupied"},
        {"id": 3, "name": "Table 3", "type": "Snooker", "status": "available"},
        {"id": 4, "name": "Table 4", "type": "8-Ball", "status": "available"},
    ]
    return {"tables": tables}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
