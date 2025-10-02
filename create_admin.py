#!/usr/bin/env python3
"""
Script to create an initial admin user for Cue Haven
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Admin
from schemas import AdminCreate
from crud import create_admin, get_admin_by_username

def create_initial_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = get_admin_by_username(db, "admin")
        if existing_admin:
            print("ℹ️  Admin user already exists.")
            return

        # Create initial admin
        admin_data = AdminCreate(
            username="admin",
            email="admin@cuehaven.com",
            full_name="System Administrator",
            password="admin123",  # Change this in production!
            is_active=True,
            is_superuser=True
        )

        admin = create_admin(db, admin_data)
        print("✅ Initial admin user created successfully!")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Password: admin123")
        print("\n⚠️  Please change the default password after first login!")

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_admin()
