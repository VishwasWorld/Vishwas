from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import jwt
from passlib.context import CryptContext
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT and Password settings
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'vishwas-world-tech-secret-key-2024')
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app
app = FastAPI(title="Vishwas World Tech HRMS", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Helper functions
def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str) and 'T' in value:
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
    return item

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Pydantic Models
class Employee(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    full_name: str
    department: str
    designation: str
    join_date: datetime
    manager: str = ""
    contact_number: str
    email_address: str
    address: str
    basic_salary: float
    status: str = "Active"  # Active, Inactive
    username: str
    password_hash: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EmployeeCreate(BaseModel):
    employee_id: str
    full_name: str
    department: str
    designation: str
    join_date: datetime
    manager: str = ""
    contact_number: str
    email_address: str
    address: str
    basic_salary: float
    username: str
    password: str

class EmployeeResponse(BaseModel):
    id: str
    employee_id: str
    full_name: str
    department: str
    designation: str
    join_date: datetime
    manager: str
    contact_number: str
    email_address: str
    address: str
    basic_salary: float
    status: str
    username: str
    created_at: datetime
    updated_at: datetime

class AttendanceRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    employee_name: str
    login_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    logout_time: Optional[datetime] = None
    login_location: dict = {}  # {"latitude": float, "longitude": float, "address": str}
    logout_location: dict = {}
    date: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime('%Y-%m-%d'))
    total_hours: float = 0.0
    status: str = "Logged In"  # Logged In, Logged Out
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AttendanceLogin(BaseModel):
    employee_id: str
    location: dict

class AttendanceLogout(BaseModel):
    employee_id: str
    location: dict

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    employee: EmployeeResponse

# Authentication Routes
@api_router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    # Find employee by username
    employee_data = await db.employees.find_one({"username": login_data.username})
    
    if not employee_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not pwd_context.verify(login_data.password, employee_data["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token(
        data={"sub": employee_data["employee_id"], "username": employee_data["username"]}
    )
    
    # Remove sensitive data
    employee_data.pop("password_hash", None)
    employee_response = EmployeeResponse(**employee_data)
    
    return LoginResponse(access_token=access_token, employee=employee_response)

# Employee Management Routes
@api_router.post("/employees", response_model=EmployeeResponse)
async def create_employee(employee_data: EmployeeCreate):
    # Check if employee_id or username already exists
    existing = await db.employees.find_one({
        "$or": [
            {"employee_id": employee_data.employee_id},
            {"username": employee_data.username}
        ]
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID or username already exists")
    
    # Hash password
    password_hash = pwd_context.hash(employee_data.password)
    
    # Create employee object
    employee_dict = employee_data.dict()
    employee_dict.pop("password")
    employee_dict["password_hash"] = password_hash
    
    employee = Employee(**employee_dict)
    
    # Prepare for MongoDB
    employee_mongo = prepare_for_mongo(employee.dict())
    
    # Insert into database
    result = await db.employees.insert_one(employee_mongo)
    
    # Return employee data without password hash
    employee_dict.pop("password_hash")
    return EmployeeResponse(**employee_dict)

@api_router.get("/employees", response_model=List[EmployeeResponse])
async def get_employees(current_user: dict = Depends(verify_token)):
    employees = await db.employees.find().to_list(1000)
    
    # Remove password hashes and convert to response model
    result = []
    for emp in employees:
        emp.pop("password_hash", None)
        emp = parse_from_mongo(emp)
        result.append(EmployeeResponse(**emp))
    
    return result

@api_router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str, current_user: dict = Depends(verify_token)):
    employee = await db.employees.find_one({"employee_id": employee_id})
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee.pop("password_hash", None)
    employee = parse_from_mongo(employee)
    return EmployeeResponse(**employee)

# Attendance Management Routes
@api_router.post("/attendance/login")
async def employee_login(attendance_data: AttendanceLogin, current_user: dict = Depends(verify_token)):
    # Check if employee exists
    employee = await db.employees.find_one({"employee_id": attendance_data.employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if already logged in today
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    existing_record = await db.attendance.find_one({
        "employee_id": attendance_data.employee_id,
        "date": today,
        "status": "Logged In"
    })
    
    if existing_record:
        raise HTTPException(status_code=400, detail="Employee already logged in today")
    
    # Create attendance record
    attendance = AttendanceRecord(
        employee_id=attendance_data.employee_id,
        employee_name=employee["full_name"],
        login_location=attendance_data.location,
        date=today
    )
    
    # Prepare for MongoDB
    attendance_mongo = prepare_for_mongo(attendance.dict())
    
    # Insert into database
    await db.attendance.insert_one(attendance_mongo)
    
    return {"message": "Login recorded successfully", "login_time": attendance.login_time}

@api_router.post("/attendance/logout")
async def employee_logout(attendance_data: AttendanceLogout, current_user: dict = Depends(verify_token)):
    # Find today's attendance record
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    attendance_record = await db.attendance.find_one({
        "employee_id": attendance_data.employee_id,
        "date": today,
        "status": "Logged In"
    })
    
    if not attendance_record:
        raise HTTPException(status_code=404, detail="No active login found for today")
    
    # Calculate total hours
    logout_time = datetime.now(timezone.utc)
    login_time = datetime.fromisoformat(attendance_record["login_time"].replace('Z', '+00:00')) if isinstance(attendance_record["login_time"], str) else attendance_record["login_time"]
    total_hours = (logout_time - login_time).total_seconds() / 3600
    
    # Update attendance record
    update_data = {
        "logout_time": logout_time.isoformat(),
        "logout_location": attendance_data.location,
        "total_hours": round(total_hours, 2),
        "status": "Logged Out"
    }
    
    await db.attendance.update_one(
        {"_id": attendance_record["_id"]},
        {"$set": update_data}
    )
    
    return {"message": "Logout recorded successfully", "total_hours": round(total_hours, 2)}

@api_router.get("/attendance/today")
async def get_today_attendance(current_user: dict = Depends(verify_token)):
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    attendance_records = await db.attendance.find({"date": today}).to_list(1000)
    
    # Parse MongoDB data
    result = []
    for record in attendance_records:
        record = parse_from_mongo(record)
        result.append(record)
    
    return result

@api_router.get("/attendance/employee/{employee_id}")
async def get_employee_attendance(employee_id: str, current_user: dict = Depends(verify_token)):
    attendance_records = await db.attendance.find({"employee_id": employee_id}).sort("date", -1).to_list(100)
    
    # Parse MongoDB data
    result = []
    for record in attendance_records:
        record = parse_from_mongo(record)
        result.append(record)
    
    return result

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(verify_token)):
    # Get total employees
    total_employees = await db.employees.count_documents({"status": "Active"})
    
    # Get today's attendance
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    present_today = await db.attendance.count_documents({"date": today})
    
    # Get currently logged in
    logged_in_now = await db.attendance.count_documents({"date": today, "status": "Logged In"})
    
    return {
        "total_employees": total_employees,
        "present_today": present_today,
        "logged_in_now": logged_in_now,
        "absent_today": total_employees - present_today
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
