#!/usr/bin/env python3
"""
Script to test the complete authentication flow
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
from crud import authenticate_admin

def test_authentication():
    db = SessionLocal()
    try:
        # Test authentication with exact credentials
        username = "admin"
        password = "admin123"
        
        print(f"🔍 Testing authentication for: {username} / {password}")
        
        result = authenticate_admin(db, username, password)
        
        if result:
            print(f"✅ Authentication successful!")
            print(f"   User: {result.username}")
            print(f"   Email: {result.email}")
            print(f"   Full name: {result.full_name}")
            print(f"   Active: {result.is_active}")
        else:
            print(f"❌ Authentication failed!")
            
        # Test with wrong password
        print(f"\n🔍 Testing with wrong password...")
        result_wrong = authenticate_admin(db, username, "wrongpassword")
        print(f"   Wrong password result: {result_wrong}")

    except Exception as e:
        print(f"❌ Error during authentication test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_authentication()
