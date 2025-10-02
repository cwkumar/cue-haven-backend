from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uvicorn

# Import our modules
from database import SessionLocal, engine, Base
from models import Admin
from schemas import AdminCreate, AdminResponse, AdminLogin, Token
from crud import create_admin, authenticate_admin, get_admin_by_username
from auth import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES

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
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://127.0.0.1:5173", "http://0.0.0.0:5173"],  # SvelteKit dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# Pydantic models
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

# Authentication endpoints
@app.post("/api/auth/register", response_model=AdminResponse)
def register_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    # Check if admin already exists
    if get_admin_by_username(db, admin.username):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    return create_admin(db=db, admin=admin)

@app.post("/api/auth/login", response_model=Token)
def login_admin(admin_login: AdminLogin, db: Session = Depends(get_db)):
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

@app.get("/api/auth/me", response_model=AdminResponse)
def read_current_admin(current_admin: Admin = Depends(get_current_admin)):
    return current_admin

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
