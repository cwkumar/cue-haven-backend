#!/usr/bin/env python3
"""
Script to list all admin users
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Admin

def list_all_admins():
    db = SessionLocal()
    try:
        admins = db.query(Admin).all()
        print(f"📊 Found {len(admins)} admin users:")
        
        for admin in admins:
            print(f"\n👤 Admin ID: {admin.id}")
            print(f"   Username: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Full Name: {admin.full_name}")
            print(f"   Active: {admin.is_active}")
            print(f"   Superuser: {admin.is_superuser}")
            print(f"   Created: {admin.created_at}")
            
            # Test password
            test_result = admin.verify_password("admin123")
            print(f"   Password test: {test_result}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_all_admins()
