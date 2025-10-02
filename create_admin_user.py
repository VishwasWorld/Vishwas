#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def simple_hash(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

async def create_admin_user():
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Check if admin user already exists
    existing_admin = await db.employees.find_one({"username": "admin"})
    if existing_admin:
        print("Admin user already exists!")
        client.close()
        return
    
    # Create admin user
    admin_user = {
        "id": "admin-001",
        "employee_id": "VWT001",
        "full_name": "HR Administrator",
        "department": "HR",
        "designation": "HR Manager",
        "join_date": datetime.now(timezone.utc).isoformat(),
        "manager": "CEO",
        "contact_number": "+91-9876543210",
        "email_address": "admin@vishwasworldtech.com",
        "address": "Vishwas World Tech Pvt Ltd, Corporate Office",
        "basic_salary": 50000.0,
        "status": "Active",
        "username": "admin",
        "password_hash": pwd_context.hash("admin123"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Insert admin user
    result = await db.employees.insert_one(admin_user)
    print(f"Admin user created successfully with ID: {result.inserted_id}")
    print("Login credentials: username='admin', password='admin123'")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())