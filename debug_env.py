#!/usr/bin/env python3
"""
Test script to debug Railway environment variables
Run this to see what environment variables are available
"""
import os

print("=" * 80)
print("🔍 RAILWAY ENVIRONMENT VARIABLES DEBUG")
print("=" * 80)

print("\n📋 DATABASE-RELATED ENVIRONMENT VARIABLES:")
database_vars = {}
for key, value in os.environ.items():
    if any(term in key.upper() for term in ['DATABASE', 'POSTGRES', 'PG', 'DB']):
        # Hide sensitive data
        safe_value = value[:30] + "..." if len(value) > 30 else value
        database_vars[key] = safe_value
        print(f"   {key}: {safe_value}")

if not database_vars:
    print("   ❌ NO database-related environment variables found!")

print(f"\n🎯 SPECIFIC CHECKS:")
print(f"   DATABASE_URL: {'✅ SET' if os.environ.get('DATABASE_URL') else '❌ NOT SET'}")
print(f"   POSTGRES_URL: {'✅ SET' if os.environ.get('POSTGRES_URL') else '❌ NOT SET'}")
print(f"   PORT: {os.environ.get('PORT', '❌ NOT SET')}")

print("\n🚀 RAILWAY SERVICE INFO:")
print(f"   RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'Not detected')}")
print(f"   RAILWAY_SERVICE_NAME: {os.environ.get('RAILWAY_SERVICE_NAME', 'Not detected')}")

print("\n" + "=" * 80)
print("💡 If DATABASE_URL is NOT SET:")
print("   1. Go to Railway dashboard")
print("   2. Click your backend service")
print("   3. Go to Variables tab")
print("   4. Add: DATABASE_URL = ${{ Postgres.DATABASE_URL }}")
print("=" * 80)