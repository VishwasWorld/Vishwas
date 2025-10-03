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
from datetime import datetime, timezone, timedelta, date
import jwt
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
import base64
from document_generator import generate_offer_letter, generate_appointment_letter
from salary_calculator import SalaryCalculator, calculate_employee_salary, get_employee_attendance_days
from salary_slip_generator import generate_salary_slip
from standard_salary_slip_generator import generate_standard_salary_slip
from employee_agreement_generator import generate_employee_agreement, calculate_late_login_penalty
from communication_service import CommunicationService, create_digital_signature_info
from enhanced_features import (
    EmployeeDocument, CompanyAnnouncement, DocumentUpload, AnnouncementCreate,
    EmployeeDocumentResponse, AnnouncementResponse, save_uploaded_file, 
    get_file_as_base64, get_dashboard_theme, get_enhanced_dashboard_stats
)
from hrms_modules import (
    InterviewCandidate, InterviewCandidateCreate, InterviewCandidateResponse,
    WorkingEmployee, CompanyHoliday, CompanyHolidayCreate, CompanyHolidayResponse,
    EmployeeDatabase, DashboardStats, get_indian_national_holidays, get_dashboard_overview,
    DEPARTMENTS, DESIGNATIONS, INTERVIEW_TYPES, HOLIDAY_TYPES
)
from working_employee_management import (
    EmployeeAttendanceDetail, LateLoginPenalty, MonthlyAttendanceSummary,
    WorkingEmployeeDocument, WorkingEmployeeProfile, WorkingEmployeeDocumentUpload,
    calculate_late_penalty, calculate_working_hours, get_attendance_status,
    generate_employee_attendance_report, WORKING_EMPLOYEE_DOCUMENT_CATEGORIES
)
from fastapi import UploadFile, File

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

def simple_hash(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    return simple_hash(plain_password) == hashed_password
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
            elif isinstance(value, date):
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

class SalaryCalculationRequest(BaseModel):
    employee_id: str
    year: int = None
    month: int = None

class SalarySlipShareRequest(BaseModel):
    employee_id: str
    year: int = None
    month: int = None
    channels: List[str] = ["email", "whatsapp", "sms"]  # Default all channels

# Authentication Routes
@api_router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    # Find employee by username
    employee_data = await db.employees.find_one({"username": login_data.username})
    
    if not employee_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(login_data.password, employee_data["password_hash"]):
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
    password_hash = simple_hash(employee_data.password)
    
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
    employee_response_dict = employee.dict()
    employee_response_dict.pop("password_hash")
    return EmployeeResponse(**employee_response_dict)

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
        record.pop("_id", None)  # Remove MongoDB ObjectId
        record = parse_from_mongo(record)
        result.append(record)
    
    return result

@api_router.get("/attendance/employee/{employee_id}")
async def get_employee_attendance(employee_id: str, current_user: dict = Depends(verify_token)):
    attendance_records = await db.attendance.find({"employee_id": employee_id}).sort("date", -1).to_list(100)
    
    # Parse MongoDB data
    result = []
    for record in attendance_records:
        record.pop("_id", None)  # Remove MongoDB ObjectId
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

# Document Generation Routes
@api_router.post("/employees/{employee_id}/generate-offer-letter")
async def generate_employee_offer_letter(employee_id: str, current_user: dict = Depends(verify_token)):
    """Generate offer letter for employee"""
    employee = await db.employees.find_one({"employee_id": employee_id})
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        # Remove MongoDB ObjectId and parse dates
        employee.pop("_id", None)
        employee.pop("password_hash", None)
        employee = parse_from_mongo(employee)
        
        # Generate offer letter PDF
        pdf_base64 = generate_offer_letter(employee)
        
        return {
            "message": "Offer letter generated successfully",
            "document_type": "offer_letter",
            "employee_id": employee_id,
            "employee_name": employee["full_name"],
            "pdf_data": pdf_base64,
            "filename": f"Offer_Letter_{employee['full_name'].replace(' ', '_')}_{employee_id}.pdf"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating offer letter: {str(e)}")

@api_router.post("/employees/{employee_id}/generate-appointment-letter")
async def generate_employee_appointment_letter(employee_id: str, current_user: dict = Depends(verify_token)):
    """Generate appointment letter for employee"""
    employee = await db.employees.find_one({"employee_id": employee_id})
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        # Remove MongoDB ObjectId and parse dates
        employee.pop("_id", None)
        employee.pop("password_hash", None)
        employee = parse_from_mongo(employee)
        
        # Generate appointment letter PDF
        pdf_base64 = generate_appointment_letter(employee)
        
        return {
            "message": "Appointment letter generated successfully",
            "document_type": "appointment_letter",
            "employee_id": employee_id,
            "employee_name": employee["full_name"],
            "pdf_data": pdf_base64,
            "filename": f"Appointment_Letter_{employee['full_name'].replace(' ', '_')}_{employee_id}.pdf"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating appointment letter: {str(e)}")

# Salary Calculation Routes
@api_router.post("/employees/{employee_id}/calculate-salary")
async def calculate_employee_monthly_salary(
    employee_id: str, 
    salary_request: SalaryCalculationRequest,
    current_user: dict = Depends(verify_token)
):
    """Calculate monthly salary for employee based on attendance"""
    
    # Get employee data
    employee = await db.employees.find_one({"employee_id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Set default year/month if not provided
    now = datetime.now(timezone.utc)
    year = salary_request.year or now.year
    month = salary_request.month or now.month
    
    try:
        # Get employee attendance records
        attendance_records = await db.attendance.find({"employee_id": employee_id}).to_list(1000)
        
        # Remove MongoDB ObjectId and parse dates
        for record in attendance_records:
            record.pop("_id", None)
            record = parse_from_mongo(record)
        
        # Remove sensitive data from employee
        employee.pop("_id", None)
        employee.pop("password_hash", None)
        employee = parse_from_mongo(employee)
        
        # Calculate salary
        salary_calculation = calculate_employee_salary(employee, attendance_records, year, month)
        
        return {
            "message": "Salary calculated successfully",
            "calculation": salary_calculation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating salary: {str(e)}")

@api_router.get("/salary/working-days/{year}/{month}")
async def get_working_days(year: int, month: int, current_user: dict = Depends(verify_token)):
    """Get working days for a specific month"""
    try:
        calculator = SalaryCalculator()
        working_days = calculator.get_working_days_in_month(year, month)
        
        return {
            "year": year,
            "month": month,
            "working_days": working_days,
            "month_name": datetime(year, month, 1).strftime('%B')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating working days: {str(e)}")

@api_router.get("/employees/{employee_id}/attendance-summary/{year}/{month}")
async def get_employee_attendance_summary(
    employee_id: str, 
    year: int, 
    month: int,
    current_user: dict = Depends(verify_token)
):
    """Get attendance summary for employee for a specific month"""
    
    try:
        # Get attendance records for the month
        attendance_records = await db.attendance.find({"employee_id": employee_id}).to_list(1000)
        
        # Count present days
        present_days = get_employee_attendance_days(attendance_records, year, month)
        
        # Get working days
        calculator = SalaryCalculator()
        total_working_days = calculator.get_working_days_in_month(year, month)
        
        # Calculate attendance percentage
        attendance_percentage = (present_days / total_working_days * 100) if total_working_days > 0 else 0
        
        return {
            "employee_id": employee_id,
            "year": year,
            "month": month,
            "month_name": datetime(year, month, 1).strftime('%B'),
            "present_days": present_days,
            "total_working_days": total_working_days,
            "absent_days": total_working_days - present_days,
            "attendance_percentage": round(attendance_percentage, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting attendance summary: {str(e)}")

@api_router.get("/salary/rates")
async def get_salary_rates(current_user: dict = Depends(verify_token)):
    """Get current government salary calculation rates"""
    
    return {
        "government_rates": {
            "esi": {
                "rate": "1.75%",
                "wage_limit": 21000,
                "description": "Employee State Insurance - applicable if gross salary ≤ ₹21,000"
            },
            "pf": {
                "employee_rate": "12%",
                "employer_rate": "12%", 
                "wage_limit": 15000,
                "description": "Provident Fund - calculated on basic salary, max ₹15,000"
            },
            "professional_tax": {
                "rates": [
                    {"range": "≤ ₹10,000", "amount": "₹0"},
                    {"range": "₹10,001 - ₹15,000", "amount": "₹150"},
                    {"range": "₹15,001 - ₹25,000", "amount": "₹200"},
                    {"range": "> ₹25,000", "amount": "₹200"}
                ],
                "state": "Karnataka"
            }
        },
        "allowance_rates": {
            "hra": {
                "metro": "50% of basic salary",
                "non_metro": "40% of basic salary"
            },
            "da": "10% of basic salary",
            "medical": "₹1,250 per month",
            "transport": "₹1,600 per month"
        }
    }

@api_router.post("/employees/{employee_id}/generate-salary-slip")
async def generate_employee_salary_slip(
    employee_id: str,
    salary_request: SalaryCalculationRequest,
    current_user: dict = Depends(verify_token)
):
    """Generate salary slip PDF for employee"""
    
    # Get employee data
    employee = await db.employees.find_one({"employee_id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Set default year/month if not provided
    now = datetime.now(timezone.utc)
    year = salary_request.year or now.year
    month = salary_request.month or now.month
    
    try:
        # Get employee attendance records
        attendance_records = await db.attendance.find({"employee_id": employee_id}).to_list(1000)
        
        # Remove MongoDB ObjectId and parse dates
        for record in attendance_records:
            record.pop("_id", None)
            record = parse_from_mongo(record)
        
        # Remove sensitive data from employee
        employee.pop("_id", None)
        employee.pop("password_hash", None)
        employee = parse_from_mongo(employee)
        
        # Calculate salary
        salary_calculation = calculate_employee_salary(employee, attendance_records, year, month)
        
        # Generate standard format salary slip PDF with digital signature
        pdf_base64 = generate_standard_salary_slip(salary_calculation)
        
        # Add digital signature information
        digital_signature = create_digital_signature_info()
        
        return {
            "message": "Standard salary slip generated successfully with digital signature",
            "employee_id": employee_id,
            "employee_name": employee["full_name"],
            "month_year": f"{salary_calculation['employee_info']['calculation_month']}",
            "pdf_data": pdf_base64,
            "filename": f"Salary_Slip_{employee['full_name'].replace(' ', '_')}_{year}_{month:02d}.pdf",
            "digital_signature": digital_signature,
            "format": "Standard Indian Salary Slip Format"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating salary slip: {str(e)}")

@api_router.post("/employees/{employee_id}/generate-and-share-salary-slip")
async def generate_and_share_salary_slip(
    employee_id: str,
    salary_request: SalarySlipShareRequest,
    current_user: dict = Depends(verify_token)
):
    """Generate salary slip and share via multiple channels (Email, WhatsApp, SMS)"""
    
    # Get employee data
    employee = await db.employees.find_one({"employee_id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Set default year/month if not provided
    now = datetime.now(timezone.utc)
    year = salary_request.year or now.year
    month = salary_request.month or now.month
    
    try:
        # Get employee attendance records
        attendance_records = await db.attendance.find({"employee_id": employee_id}).to_list(1000)
        
        # Remove MongoDB ObjectId and parse dates
        for record in attendance_records:
            record.pop("_id", None)
            record = parse_from_mongo(record)
        
        # Remove sensitive data from employee
        employee.pop("_id", None)
        employee.pop("password_hash", None)
        employee = parse_from_mongo(employee)
        
        # Calculate salary
        salary_calculation = calculate_employee_salary(employee, attendance_records, year, month)
        
        # Generate standard salary slip PDF
        pdf_base64 = generate_standard_salary_slip(salary_calculation)
        
        # Create communication service
        comm_service = CommunicationService()
        
        # Send via selected channels
        sharing_results = comm_service.send_salary_slip_all_channels(
            employee, salary_calculation, pdf_base64, salary_request.channels
        )
        
        # Add digital signature information
        digital_signature = create_digital_signature_info()
        
        return {
            "message": "Salary slip generated and shared successfully",
            "employee_id": employee_id,
            "employee_name": employee["full_name"],
            "month_year": f"{salary_calculation['employee_info']['calculation_month']}",
            "sharing_results": sharing_results,
            "digital_signature": digital_signature,
            "channels_used": salary_request.channels,
            "successful_deliveries": sharing_results["successful_channels"],
            "failed_deliveries": sharing_results["failed_channels"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating and sharing salary slip: {str(e)}")

@api_router.get("/salary/employee-selection")
async def get_employees_for_salary_selection(current_user: dict = Depends(verify_token)):
    """Get employees list for salary processing selection"""
    try:
        employees = await db.employees.find({"status": "Active"}).to_list(1000)
        
        # Format for selection dropdown
        employee_list = []
        for emp in employees:
            emp.pop("_id", None)
            emp.pop("password_hash", None)
            employee_list.append({
                "employee_id": emp["employee_id"],
                "full_name": emp["full_name"],
                "department": emp["department"],
                "designation": emp["designation"],
                "email_address": emp["email_address"],
                "contact_number": emp["contact_number"],
                "basic_salary": emp["basic_salary"]
            })
        
        return {
            "employees": employee_list,
            "total_count": len(employee_list),
            "message": "Employee list retrieved for salary processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching employees for salary selection: {str(e)}")

@api_router.get("/salary/communication-channels")
async def get_available_communication_channels():
    """Get available communication channels for salary slip sharing"""
    return {
        "channels": [
            {
                "id": "email",
                "name": "Email",
                "description": "Send detailed salary slip PDF via email",
                "icon": "📧",
                "recommended": True
            },
            {
                "id": "whatsapp",
                "name": "WhatsApp",
                "description": "Send notification with summary via WhatsApp Business",
                "icon": "📱",
                "recommended": True
            },
            {
                "id": "sms",
                "name": "SMS",
                "description": "Send basic notification via SMS",
                "icon": "💬",
                "recommended": False
            }
        ],
        "default_selection": ["email", "whatsapp"],
        "note": "Email includes PDF attachment, WhatsApp and SMS provide notifications only"
    }

# Enhanced Employee Management Routes
@api_router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str, current_user: dict = Depends(verify_token)):
    """Delete employee and related data"""
    try:
        # Check if employee exists
        employee = await db.employees.find_one({"employee_id": employee_id})
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Delete employee from database
        await db.employees.delete_one({"employee_id": employee_id})
        
        # Delete related attendance records (optional - keep for audit trail)
        # await db.attendance.delete_many({"employee_id": employee_id})
        
        # Delete related documents (optional - keep for audit trail)  
        # await db.employee_documents.delete_many({"employee_id": employee_id})
        
        return {
            "message": f"Employee {employee.get('full_name', 'Unknown')} (ID: {employee_id}) deleted successfully",
            "deleted_employee": {
                "employee_id": employee_id,
                "full_name": employee.get("full_name", "Unknown"),
                "department": employee.get("department", "Unknown")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting employee: {str(e)}")

# Document Management Routes
@api_router.post("/employees/{employee_id}/upload-document")
async def upload_employee_document(
    employee_id: str,
    document_type: str,
    description: str = "",
    file: UploadFile = File(...),
    current_user: dict = Depends(verify_token)
):
    """Upload document for employee"""
    try:
        # Verify employee exists
        employee = await db.employees.find_one({"employee_id": employee_id})
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Validate file type
        allowed_extensions = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Save file
        file_path, file_size = save_uploaded_file(file, employee_id, document_type)
        
        # Create document record
        document = EmployeeDocument(
            employee_id=employee_id,
            document_type=document_type,
            document_name=file.filename,
            file_path=file_path,
            file_size=file_size,
            uploaded_by=current_user.get("username", "system"),
            description=description
        )
        
        # Prepare for MongoDB
        document_mongo = prepare_for_mongo(document.dict())
        
        # Insert into database
        await db.employee_documents.insert_one(document_mongo)
        
        return {
            "message": "Document uploaded successfully",
            "document": EmployeeDocumentResponse(
                id=document.id,
                employee_id=document.employee_id,
                document_type=document.document_type,
                document_name=document.document_name,
                file_size=document.file_size,
                uploaded_by=document.uploaded_by,
                uploaded_at=document.uploaded_at,
                description=document.description
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@api_router.get("/employees/{employee_id}/documents", response_model=List[EmployeeDocumentResponse])
async def get_employee_documents(employee_id: str, current_user: dict = Depends(verify_token)):
    """Get all documents for an employee"""
    try:
        documents = await db.employee_documents.find({"employee_id": employee_id}).to_list(1000)
        
        result = []
        for doc in documents:
            doc.pop("_id", None)
            doc.pop("file_path", None)  # Don't expose file path
            doc = parse_from_mongo(doc)
            result.append(EmployeeDocumentResponse(**doc))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching employee documents: {str(e)}")

@api_router.get("/employees/{employee_id}/documents/{document_id}/download")
async def download_employee_document(
    employee_id: str, 
    document_id: str, 
    current_user: dict = Depends(verify_token)
):
    """Download employee document"""
    try:
        # Find document
        document = await db.employee_documents.find_one({
            "id": document_id,
            "employee_id": employee_id
        })
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get file content as base64
        file_base64 = get_file_as_base64(document["file_path"])
        
        return {
            "document_name": document["document_name"],
            "document_type": document["document_type"],
            "file_data": file_base64,
            "file_size": document["file_size"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")

# Company Announcements Routes
@api_router.post("/announcements", response_model=AnnouncementResponse)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    current_user: dict = Depends(verify_token)
):
    """Create company announcement"""
    try:
        announcement = CompanyAnnouncement(
            title=announcement_data.title,
            content=announcement_data.content,
            announcement_type=announcement_data.announcement_type,
            priority=announcement_data.priority,
            published_by=current_user.get("username", "system"),
            valid_until=announcement_data.valid_until,
            target_departments=announcement_data.target_departments
        )
        
        # Prepare for MongoDB
        announcement_mongo = prepare_for_mongo(announcement.dict())
        
        # Insert into database
        await db.announcements.insert_one(announcement_mongo)
        
        # Remove MongoDB fields for response
        announcement_dict = announcement.dict()
        return AnnouncementResponse(**announcement_dict)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating announcement: {str(e)}")

@api_router.get("/announcements", response_model=List[AnnouncementResponse])
async def get_announcements(current_user: dict = Depends(verify_token)):
    """Get all active announcements"""
    try:
        # Get active announcements, sorted by priority and date
        announcements = await db.announcements.find({
            "is_active": True,
            "$or": [
                {"valid_until": {"$gt": datetime.now(timezone.utc)}},
                {"valid_until": None}
            ]
        }).sort([("priority", -1), ("published_at", -1)]).to_list(100)
        
        result = []
        for ann in announcements:
            ann.pop("_id", None)
            ann = parse_from_mongo(ann)
            result.append(AnnouncementResponse(**ann))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching announcements: {str(e)}")

@api_router.delete("/announcements/{announcement_id}")
async def delete_announcement(announcement_id: str, current_user: dict = Depends(verify_token)):
    """Delete announcement"""
    try:
        # Soft delete (set inactive)
        result = await db.announcements.update_one(
            {"id": announcement_id},
            {"$set": {"is_active": False}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Announcement not found")
        
        return {"message": "Announcement deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting announcement: {str(e)}")

# Enhanced Dashboard Routes
@api_router.get("/dashboard/theme")
async def get_dashboard_theme_config():
    """Get dashboard theme configuration"""
    return get_dashboard_theme()

@api_router.get("/dashboard/enhanced-stats")
async def get_enhanced_dashboard_statistics(current_user: dict = Depends(verify_token)):
    """Get comprehensive dashboard statistics"""
    try:
        # Get basic stats
        total_employees = await db.employees.count_documents({"status": "Active"})
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        present_today = await db.attendance.count_documents({"date": today})
        logged_in_now = await db.attendance.count_documents({"date": today, "status": "Logged In"})
        
        # Get enhanced stats
        total_documents = await db.employee_documents.count_documents({})
        active_announcements = await db.announcements.count_documents({"is_active": True})
        
        # Get recent stats (last 7 days)
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7))
        recent_documents = await db.employee_documents.count_documents({
            "uploaded_at": {"$gte": week_ago}
        })
        recent_announcements = await db.announcements.count_documents({
            "published_at": {"$gte": week_ago}
        })
        
        # Get urgent announcements
        urgent_announcements = await db.announcements.count_documents({
            "is_active": True,
            "priority": "Urgent"
        })
        
        return {
            "employee_metrics": {
                "total_employees": total_employees,
                "present_today": present_today,
                "logged_in_now": logged_in_now,
                "absent_today": total_employees - present_today
            },
            "document_metrics": {
                "total_documents": total_documents,
                "recent_uploads": recent_documents,
                "pending_documents": 0  # Can be enhanced based on requirements
            },
            "announcement_metrics": {
                "active_announcements": active_announcements,
                "recent_announcements": recent_announcements,
                "urgent_announcements": urgent_announcements
            },
            "system_health": {
                "database_status": "Connected",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching enhanced dashboard stats: {str(e)}")

@api_router.post("/employees/{employee_id}/generate-employee-agreement")
async def generate_employee_agreement_document(employee_id: str, current_user: dict = Depends(verify_token)):
    """Generate comprehensive employee agreement with legal terms"""
    employee = await db.employees.find_one({"employee_id": employee_id})
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        # Remove MongoDB ObjectId and parse dates
        employee.pop("_id", None)
        employee.pop("password_hash", None)
        employee = parse_from_mongo(employee)
        
        # Generate employee agreement PDF
        pdf_base64 = generate_employee_agreement(employee)
        
        return {
            "message": "Employee agreement generated successfully",
            "document_type": "employee_agreement",
            "employee_id": employee_id,
            "employee_name": employee["full_name"],
            "pdf_data": pdf_base64,
            "filename": f"Employee_Agreement_{employee['full_name'].replace(' ', '_')}_{employee_id}.pdf"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating employee agreement: {str(e)}")

@api_router.post("/attendance/calculate-late-penalty")
async def calculate_late_penalty(
    employee_id: str, 
    login_time: str, 
    current_user: dict = Depends(verify_token)
):
    """Calculate penalty for late login"""
    try:
        penalty_info = calculate_late_login_penalty(login_time)
        
        return {
            "employee_id": employee_id,
            "login_time": login_time,
            "scheduled_time": "09:45",
            "penalty_amount": penalty_info["penalty"],
            "delay_minutes": penalty_info["delay_minutes"],
            "category": penalty_info["category"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating late penalty: {str(e)}")

@api_router.get("/company/policy")
async def get_company_policy(current_user: dict = Depends(verify_token)):
    """Get company policies and information"""
    
    return {
        "company_info": {
            "name": "Vishwas World Tech Private Limited",
            "address": "100 DC Complex, Chandra Layout, Bangalore - 560040",
            "phone": "+91-80-12345678",
            "email": "hr@vishwasworldtech.com",
            "working_hours": {
                "start_time": "09:45 AM",
                "end_time": "06:45 PM",
                "lunch_break": "1 hour (as designated)",
                "working_days": "Monday to Friday"
            }
        },
        "attendance_policy": {
            "location_tracking": "Mandatory GPS-based attendance",
            "late_login_penalties": [
                {"range": "Up to 15 minutes", "penalty": "₹0 (Grace period)"},
                {"range": "16-30 minutes", "penalty": "₹200 per occurrence"},
                {"range": "31-60 minutes", "penalty": "₹500 per occurrence"},
                {"range": "More than 60 minutes", "penalty": "₹1,000 per occurrence"},
                {"range": "More than 3 late arrivals/month", "penalty": "Additional ₹1,500"}
            ]
        },
        "salary_policy": {
            "calculation_basis": "Attendance-based pro-rata calculation",
            "deductions": {
                "pf": "12% of basic salary",
                "esi": "1.75% if gross ≤ ₹21,000",
                "professional_tax": "₹200 (Karnataka)",
                "late_penalties": "As per attendance policy"
            },
            "allowances": {
                "hra": "50% of basic (Metro rate)",
                "da": "10% of basic",
                "medical": "₹1,250/month",
                "transport": "₹1,600/month"
            }
        }
    }

# ==============================
# NEW ENHANCED HRMS MODULES API ENDPOINTS
# ==============================

# Interview Scheduling Routes
@api_router.post("/interviews", response_model=InterviewCandidateResponse)
async def create_interview(
    interview_data: InterviewCandidateCreate,
    current_user: dict = Depends(verify_token)
):
    """Schedule new interview for candidate"""
    try:
        interview = InterviewCandidate(
            **interview_data.dict(),
            created_by=current_user.get("username", "system")
        )
        
        interview_mongo = prepare_for_mongo(interview.dict())
        await db.interviews.insert_one(interview_mongo)
        
        interview_dict = interview.dict()
        return InterviewCandidateResponse(**interview_dict)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating interview: {str(e)}")

@api_router.get("/interviews", response_model=List[InterviewCandidateResponse])
async def get_interviews(
    status: str = None,
    department: str = None,
    current_user: dict = Depends(verify_token)
):
    """Get scheduled interviews with optional filters"""
    try:
        query = {}
        if status:
            query["interview_status"] = status
        if department:
            query["department"] = department
        
        interviews = await db.interviews.find(query).sort("interview_date", 1).to_list(100)
        
        result = []
        for interview in interviews:
            interview.pop("_id", None)
            interview = parse_from_mongo(interview)
            result.append(InterviewCandidateResponse(**interview))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching interviews: {str(e)}")

@api_router.put("/interviews/{interview_id}")
async def update_interview_status(
    interview_id: str,
    status: str,
    notes: str = "",
    current_user: dict = Depends(verify_token)
):
    """Update interview status and notes"""
    try:
        update_data = {
            "interview_status": status,
            "interview_notes": notes,
            "updated_at": datetime.now(timezone.utc)
        }
        
        result = await db.interviews.update_one(
            {"id": interview_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        return {"message": "Interview status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating interview: {str(e)}")

# Working Employee Database Routes
@api_router.get("/working-employees", response_model=List[dict])
async def get_working_employees(
    department: str = None,
    current_user: dict = Depends(verify_token)
):
    """Get detailed working employee database"""
    try:
        query = {"status": "Active"}
        if department:
            query["department"] = department
        
        employees = await db.employees.find(query).to_list(None)
        
        result = []
        for emp in employees:
            emp.pop("_id", None)
            emp.pop("password_hash", None)
            emp = parse_from_mongo(emp)
            
            # Get latest attendance for each employee
            latest_attendance = await db.attendance.find_one(
                {"employee_id": emp["employee_id"]},
                sort=[("date", -1)]
            )
            
            # Clean attendance data if exists
            if latest_attendance:
                latest_attendance.pop("_id", None)
                latest_attendance = parse_from_mongo(latest_attendance)
            
            # Get document completion status
            emp_documents = await db.employee_documents.find(
                {"employee_id": emp["employee_id"]}
            ).to_list(None)
            
            document_types = [doc.get("document_type", "") for doc in emp_documents]
            completion_percentage = calculate_document_completion_percentage(document_types)
            
            # Enhanced employee profile
            enhanced_employee = {
                **emp,
                "latest_attendance": latest_attendance,
                "document_completion": completion_percentage,
                "total_documents": len(emp_documents),
                "last_login": latest_attendance.get("login_time") if latest_attendance else None
            }
            
            result.append(enhanced_employee)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching working employees: {str(e)}")

@api_router.get("/working-employees/{employee_id}/attendance-report")
async def get_employee_attendance_report(
    employee_id: str,
    month: int,
    year: int,
    current_user: dict = Depends(verify_token)
):
    """Get detailed attendance report for working employee"""
    try:
        # Get all attendance records for the employee
        attendance_records = await db.attendance.find({
            "employee_id": employee_id
        }).to_list(None)
        
        # Convert MongoDB records to dict format
        records = []
        for record in attendance_records:
            record.pop("_id", None)
            record = parse_from_mongo(record)
            records.append(record)
        
        # Generate comprehensive report
        report = generate_employee_attendance_report(employee_id, month, year, records)
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating attendance report: {str(e)}")

# Holiday Calendar Routes
@api_router.post("/holidays", response_model=CompanyHolidayResponse)
async def create_holiday(
    holiday_data: CompanyHolidayCreate,
    current_user: dict = Depends(verify_token)
):
    """Add company holiday to calendar"""
    try:
        holiday = CompanyHoliday(
            **holiday_data.dict(),
            created_by=current_user.get("username", "system")
        )
        
        holiday_mongo = prepare_for_mongo(holiday.dict())
        await db.holidays.insert_one(holiday_mongo)
        
        holiday_dict = holiday.dict()
        return CompanyHolidayResponse(**holiday_dict)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating holiday: {str(e)}")

@api_router.get("/holidays/{year}")
async def get_yearly_holidays(
    year: int,
    current_user: dict = Depends(verify_token)
):
    """Get complete holiday calendar for a year"""
    try:
        # Get custom company holidays
        custom_holidays = await db.holidays.find({
            "$expr": {"$eq": [{"$year": "$holiday_date"}, year]}
        }).to_list(None)
        
        # Get Indian national holidays
        national_holidays = get_indian_national_holidays(year)
        
        # Process custom holidays
        custom_holiday_list = []
        for holiday in custom_holidays:
            holiday.pop("_id", None)
            holiday = parse_from_mongo(holiday)
            custom_holiday_list.append(CompanyHolidayResponse(**holiday))
        
        # Combine all holidays
        all_holidays = custom_holiday_list + [
            CompanyHolidayResponse(
                id=str(uuid.uuid4()),
                holiday_name=h["name"],
                holiday_date=datetime.strptime(h["date"], "%Y-%m-%d").date(),
                holiday_type=h["type"],
                description=f"Indian {h['type']} Holiday",
                is_mandatory=True,
                applicable_locations=["All"],
                created_at=datetime.now(timezone.utc)
            ) for h in national_holidays
        ]
        
        # Sort by date
        all_holidays.sort(key=lambda x: x.holiday_date)
        
        return {
            "year": year,
            "holidays": all_holidays,
            "total_holidays": len(all_holidays),
            "mandatory_holidays": len([h for h in all_holidays if h.is_mandatory]),
            "optional_holidays": len([h for h in all_holidays if not h.is_mandatory])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching holiday calendar: {str(e)}")

# Enhanced Dashboard Overview
@api_router.get("/dashboard/overview")
async def get_dashboard_overview_data(current_user: dict = Depends(verify_token)):
    """Get comprehensive dashboard overview with all modules"""
    try:
        overview = get_dashboard_overview()
        
        # Get actual statistics for each module
        stats = {
            "employee_database": await db.employees.count_documents({}),
            "interview_scheduled": await db.interviews.count_documents({"interview_status": {"$ne": "Completed"}}),
            "working_employees": await db.employees.count_documents({"status": "Active"}),
            "announcements": await db.announcements.count_documents({"is_active": True}),
            "holidays": await db.holidays.count_documents({})
        }
        
        return {
            **overview,
            "statistics": stats,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard overview: {str(e)}")

# Digital Salary Slip with Signature
@api_router.post("/employees/{employee_id}/generate-digital-salary-slip")
async def generate_digital_salary_slip_with_signature(
    employee_id: str,
    month: int,
    year: int,
    current_user: dict = Depends(verify_token)
):
    """Generate salary slip with digital signature and QR code"""
    try:
        employee = await db.employees.find_one({"employee_id": employee_id})
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee.pop("_id", None)
        employee.pop("password_hash", None)
        employee = parse_from_mongo(employee)
        
        # Generate digital signature info
        signature_info = create_digital_signature_info(employee_id, month, year)
        
        # Generate standard salary slip with digital signature
        pdf_base64 = generate_standard_salary_slip(employee, month, year, signature_info)
        
        return {
            "message": "Digital salary slip generated successfully",
            "employee_id": employee_id,
            "employee_name": employee["full_name"],
            "month": month,
            "year": year,
            "pdf_data": pdf_base64,
            "filename": f"Digital_Salary_Slip_{employee['full_name'].replace(' ', '_')}_{month}_{year}.pdf",
            "digital_signature": signature_info,
            "sharing_channels": ["email", "whatsapp", "sms"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating digital salary slip: {str(e)}")

# Multi-channel Salary Slip Sharing Request Model
class SalarySlipShareRequest(BaseModel):
    month: int
    year: int
    channels: List[str]  # ["email", "whatsapp", "sms"]

@api_router.post("/employees/{employee_id}/share-salary-slip")
async def share_salary_slip_multi_channel(
    employee_id: str,
    request: SalarySlipShareRequest,
    current_user: dict = Depends(verify_token)
):
    """Share salary slip via multiple communication channels"""
    try:
        employee = await db.employees.find_one({"employee_id": employee_id})
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee.pop("_id", None)
        employee.pop("password_hash", None)
        employee = parse_from_mongo(employee)
        
        # Initialize communication service
        comm_service = CommunicationService()
        
        # Generate digital salary slip
        signature_info = create_digital_signature_info(employee_id, month, year)
        pdf_base64 = generate_standard_salary_slip(employee, month, year, signature_info)
        
        # Share via selected channels
        sharing_results = {}
        
        for channel in channels:
            try:
                if channel == "email":
                    result = await comm_service.send_salary_slip_email(
                        employee, pdf_base64, month, year
                    )
                elif channel == "whatsapp":
                    result = await comm_service.send_salary_slip_whatsapp(
                        employee, month, year, signature_info
                    )
                elif channel == "sms":
                    result = await comm_service.send_salary_slip_sms(
                        employee, month, year
                    )
                else:
                    result = {"status": "error", "message": f"Unknown channel: {channel}"}
                
                sharing_results[channel] = result
                
            except Exception as channel_error:
                sharing_results[channel] = {
                    "status": "error",
                    "message": str(channel_error)
                }
        
        return {
            "message": "Salary slip sharing completed",
            "employee_id": employee_id,
            "employee_name": employee["full_name"],
            "month": month,
            "year": year,
            "channels_attempted": channels,
            "sharing_results": sharing_results,
            "overall_status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sharing salary slip: {str(e)}")

# Helper function for document completion calculation
def calculate_document_completion_percentage(uploaded_document_types: List[str]) -> float:
    """Calculate document completion percentage for working employees"""
    total_required = 0
    uploaded_required = 0
    
    for category, details in WORKING_EMPLOYEE_DOCUMENT_CATEGORIES.items():
        total_required += len(details["required"])
        for doc_type in details["required"]:
            if doc_type in uploaded_document_types:
                uploaded_required += 1
    
    if total_required == 0:
        return 100.0
    
    return round((uploaded_required / total_required) * 100, 2)

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
