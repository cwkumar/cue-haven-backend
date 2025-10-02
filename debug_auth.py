#!/usr/bin/env python3
"""
Script to debug the admin user password
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Admin
from crud import get_admin_by_username
import bcrypt

def debug_admin_password():
    db = SessionLocal()
    try:
        # Get the admin user
        admin = get_admin_by_username(db, "admin")
        if not admin:
            print("❌ Admin user not found")
            return

        print(f"✅ Admin user found: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Stored hash: {admin.hashed_password}")
        print(f"   Hash type: {type(admin.hashed_password)}")
        print(f"   Hash length: {len(admin.hashed_password)}")

        # Test password verification
        test_password = "admin123"
        print(f"\n🔍 Testing password verification with: '{test_password}'")
        
        # Manual verification
        try:
            is_valid = bcrypt.checkpw(test_password.encode('utf-8'), admin.hashed_password.encode('utf-8'))
            print(f"   Manual bcrypt check: {is_valid}")
        except Exception as e:
            print(f"   Manual bcrypt error: {e}")

        # Using model method
        try:
            is_valid_model = admin.verify_password(test_password)
            print(f"   Model method check: {is_valid_model}")
        except Exception as e:
            print(f"   Model method error: {e}")

        # Test hash creation
        print(f"\n🔧 Testing hash creation:")
        new_hash = Admin.hash_password(test_password)
        print(f"   New hash: {new_hash}")
        print(f"   New hash type: {type(new_hash)}")
        
        # Test new hash verification
        try:
            is_new_valid = bcrypt.checkpw(test_password.encode('utf-8'), new_hash.encode('utf-8'))
            print(f"   New hash verification: {is_new_valid}")
        except Exception as e:
            print(f"   New hash verification error: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_admin_password()
