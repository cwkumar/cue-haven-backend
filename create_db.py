#!/usr/bin/env python3
"""
Script to create the PostgreSQL database for Cue Haven
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def create_database():
    try:
        # Connect to PostgreSQL server (postgres database)
        connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="password"
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'cuehaven'")
        exists = cursor.fetchone()
        
        if not exists:
            # Create the database
            cursor.execute("CREATE DATABASE cuehaven")
            print("✅ Database 'cuehaven' created successfully!")
        else:
            print("ℹ️  Database 'cuehaven' already exists.")
            
        cursor.close()
        connection.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        print("Make sure PostgreSQL is running and credentials are correct.")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
