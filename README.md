# Cue Haven Backend

FastAPI backend for the Cue Haven Billiards Club application.

## Features

- RESTful API for table bookings
- Tournament management
- Table availability tracking
- CORS enabled for frontend integration

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python main.py
```

The API will be available at:
- Main API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## API Endpoints

### General
- `GET /` - Welcome message
- `GET /health` - Health check

### Bookings
- `GET /api/bookings` - Get all bookings
- `POST /api/bookings` - Create a new booking
- `GET /api/bookings/{id}` - Get booking by ID

### Tournaments
- `GET /api/tournaments` - Get all tournaments
- `POST /api/tournaments` - Create a new tournament
- `GET /api/tournaments/{id}` - Get tournament by ID

### Tables
- `GET /api/tables` - Get available tables

## Development

The server runs with auto-reload enabled for development. Any changes to the code will automatically restart the server.
