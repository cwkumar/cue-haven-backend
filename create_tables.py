#!/usr/bin/env python3
"""
Script to create database tables on Railway deployment
"""
import os
from database import engine, Base
from models import admin, table_session, inventory_item

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()