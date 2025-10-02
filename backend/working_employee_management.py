from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone, date, time
import uuid

# Working Employee Attendance Models
class EmployeeAttendanceDetail(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    employee_name: str
    date: date
    login_time: Optional[time] = None
    logout_time: Optional[time] = None
    scheduled_login: time = time(9, 45)  # 9:45 AM
    scheduled_logout: time = time(18, 45)  # 6:45 PM
    late_minutes: int = 0
    early_departure_minutes: int = 0
    total_working_hours: float = 0.0
    overtime_hours: float = 0.0
    status: str = "Absent"  # "Present", "Absent", "Late", "Half Day", "On Leave"
    late_penalty_amount: float = 0.0
    location_login: dict = {}
    location_logout: dict = {}
    remarks: str = ""
    approved_by: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LateLoginPenalty(BaseModel):
    employee_id: str
    date: date
    scheduled_time: time
    actual_login_time: time
    late_minutes: int
    penalty_amount: float
    penalty_category: str  # "Grace Period", "Minor Late", "Major Late", "Severe Late"
    month: int
    year: int

class MonthlyAttendanceSummary(BaseModel):
    employee_id: str
    employee_name: str
    month: int
    year: int
    total_working_days: int
    present_days: int
    absent_days: int
    late_days: int
    on_leave_days: int
    total_late_minutes: int
    total_penalty_amount: float
    attendance_percentage: float
    punctuality_score: float
    overtime_hours: float

# Working Employee Document Models
class WorkingEmployeeDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    employee_name: str
    document_category: str  # "Personal", "Educational", "Previous Employment", "Identity"
    document_type: str
    document_name: str
    file_path: str
    file_size: int
    upload_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uploaded_by: str
    verification_status: str = "Pending"  # "Pending", "Verified", "Rejected"
    verified_by: str = ""
    verification_date: Optional[datetime] = None
    expiry_date: Optional[date] = None
    is_mandatory: bool = True
    remarks: str = ""

class DocumentCategory(BaseModel):
    category_name: str
    category_description: str
    required_documents: List[str]
    optional_documents: List[str]

# Working Employee Profile Enhancement
class WorkingEmployeeProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    full_name: str
    department: str
    designation: str
    join_date: date
    email_address: str
    contact_number: str
    basic_salary: float
    current_status: str = "Active"
    work_location: str = "Office"
    shift_timing: str = "9:45 AM - 6:45 PM"
    reporting_manager: str = ""
    team_lead: str = ""
    current_project: str = ""
    employee_code: str = ""
    probation_status: str = "Completed"  # "In Progress", "Completed", "Extended"
    confirmation_date: Optional[date] = None
    last_working_day: Optional[date] = None
    exit_reason: str = ""
    performance_rating: str = "Good"
    documents_complete: bool = False
    document_completion_percentage: float = 0.0
    total_experience: str = ""
    skills: List[str] = []
    emergency_contact_name: str = ""
    emergency_contact_number: str = ""
    emergency_contact_relation: str = ""
    permanent_address: str = ""
    current_address: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request Models
class WorkingEmployeeDocumentUpload(BaseModel):
    employee_id: str
    document_category: str
    document_type: str
    document_name: str
    is_mandatory: bool = True
    expiry_date: Optional[date] = None
    remarks: str = ""

class AttendanceFilterRequest(BaseModel):
    employee_id: Optional[str] = None
    department: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status_filter: Optional[str] = None

# Document Categories Configuration
WORKING_EMPLOYEE_DOCUMENT_CATEGORIES = {
    "Personal Documents": {
        "description": "Personal identification and address documents",
        "required": [
            "Aadhar Card",
            "PAN Card", 
            "Passport Size Photo",
            "Address Proof"
        ],
        "optional": [
            "Passport",
            "Driving License",
            "Voter ID"
        ]
    },
    "Educational Documents": {
        "description": "Educational qualifications and certificates",
        "required": [
            "10th Mark Sheet",
            "12th Mark Sheet",
            "Graduation Certificate",
            "Final Mark Sheet/Transcript"
        ],
        "optional": [
            "Post Graduation Certificate",
            "Professional Certifications",
            "Additional Courses",
            "Technical Certifications"
        ]
    },
    "Previous Employment": {
        "description": "Previous company documents and experience letters",
        "required": [
            "Resume/CV",
            "Experience Letter"
        ],
        "optional": [
            "Previous Company Offer Letter",
            "Previous Company Appointment Letter", 
            "Previous Company Salary Slips",
            "Relieving Letter",
            "Service Certificate",
            "Recommendation Letter"
        ]
    },
    "Current Employment": {
        "description": "Current company employment documents",
        "required": [
            "Updated Resume",
            "Joining Form",
            "Employee Agreement"
        ],
        "optional": [
            "Medical Certificate",
            "Background Verification",
            "Reference Checks"
        ]
    }
}

# Late Login Penalty Configuration
LATE_LOGIN_PENALTY_STRUCTURE = {
    "grace_period_minutes": 15,
    "penalty_structure": [
        {
            "category": "Grace Period",
            "min_minutes": 0,
            "max_minutes": 15,
            "penalty_amount": 0,
            "description": "No penalty - Grace period"
        },
        {
            "category": "Minor Late", 
            "min_minutes": 16,
            "max_minutes": 30,
            "penalty_amount": 200,
            "description": "Minor lateness penalty"
        },
        {
            "category": "Major Late",
            "min_minutes": 31,
            "max_minutes": 60, 
            "penalty_amount": 500,
            "description": "Major lateness penalty"
        },
        {
            "category": "Severe Late",
            "min_minutes": 61,
            "max_minutes": 999,
            "penalty_amount": 1000,
            "description": "Severe lateness penalty"
        }
    ],
    "monthly_late_limit": 3,
    "monthly_excess_penalty": 1500,
    "consecutive_late_penalty": 2000
}

def calculate_late_penalty(late_minutes: int, monthly_late_count: int = 0) -> Dict:
    """Calculate penalty for late login based on company policy"""
    penalty_info = {
        "late_minutes": late_minutes,
        "penalty_amount": 0,
        "category": "On Time",
        "additional_penalty": 0,
        "total_penalty": 0
    }
    
    # Find appropriate penalty category
    for category in LATE_LOGIN_PENALTY_STRUCTURE["penalty_structure"]:
        if category["min_minutes"] <= late_minutes <= category["max_minutes"]:
            penalty_info["penalty_amount"] = category["penalty_amount"]
            penalty_info["category"] = category["category"]
            break
    
    # Additional penalty for monthly excess
    if monthly_late_count > LATE_LOGIN_PENALTY_STRUCTURE["monthly_late_limit"]:
        penalty_info["additional_penalty"] = LATE_LOGIN_PENALTY_STRUCTURE["monthly_excess_penalty"]
    
    penalty_info["total_penalty"] = penalty_info["penalty_amount"] + penalty_info["additional_penalty"]
    
    return penalty_info

def calculate_working_hours(login_time: time, logout_time: time) -> Dict:
    """Calculate working hours and overtime"""
    if not login_time or not logout_time:
        return {"working_hours": 0, "overtime_hours": 0}
    
    # Convert to datetime for calculation
    login_datetime = datetime.combine(date.today(), login_time)
    logout_datetime = datetime.combine(date.today(), logout_time)
    
    # Handle next day logout
    if logout_datetime < login_datetime:
        logout_datetime = datetime.combine(date.today() + timedelta(days=1), logout_time)
    
    total_minutes = (logout_datetime - login_datetime).total_seconds() / 60
    
    # Subtract lunch break (1 hour)
    working_minutes = max(0, total_minutes - 60)
    working_hours = working_minutes / 60
    
    # Standard working hours (9 hours including lunch)
    standard_hours = 8
    overtime_hours = max(0, working_hours - standard_hours)
    
    return {
        "working_hours": round(working_hours, 2),
        "overtime_hours": round(overtime_hours, 2)
    }

def get_attendance_status(login_time: Optional[time], logout_time: Optional[time], 
                         scheduled_login: time, late_minutes: int) -> str:
    """Determine attendance status"""
    if not login_time:
        return "Absent"
    
    if late_minutes > 0:
        return "Late"
    
    if not logout_time:
        return "Present"  # Still working
    
    return "Present"

def calculate_punctuality_score(late_days: int, total_working_days: int) -> float:
    """Calculate punctuality score (0-100)"""
    if total_working_days == 0:
        return 100.0
    
    on_time_days = total_working_days - late_days
    score = (on_time_days / total_working_days) * 100
    return round(score, 2)

def get_document_completion_percentage(employee_id: str, uploaded_docs: List[str]) -> float:
    """Calculate document completion percentage"""
    total_required = 0
    uploaded_required = 0
    
    for category, details in WORKING_EMPLOYEE_DOCUMENT_CATEGORIES.items():
        total_required += len(details["required"])
        for doc_type in details["required"]:
            if doc_type in uploaded_docs:
                uploaded_required += 1
    
    if total_required == 0:
        return 100.0
    
    percentage = (uploaded_required / total_required) * 100
    return round(percentage, 2)

def generate_employee_attendance_report(employee_id: str, month: int, year: int, 
                                      attendance_records: List[dict]) -> Dict:
    """Generate comprehensive attendance report for an employee"""
    
    # Filter records for the specified month/year
    month_records = []
    for record in attendance_records:
        record_date = record.get('date')
        if isinstance(record_date, str):
            record_date = datetime.fromisoformat(record_date).date()
        
        if record_date.month == month and record_date.year == year:
            month_records.append(record)
    
    # Calculate statistics
    total_working_days = len(month_records) if month_records else 22  # Default
    present_days = len([r for r in month_records if r.get('status') in ['Present', 'Late']])
    absent_days = total_working_days - present_days
    late_days = len([r for r in month_records if r.get('status') == 'Late'])
    
    total_late_minutes = sum([r.get('late_minutes', 0) for r in month_records])
    total_penalty = sum([r.get('late_penalty_amount', 0) for r in month_records])
    
    attendance_percentage = (present_days / total_working_days * 100) if total_working_days > 0 else 0
    punctuality_score = calculate_punctuality_score(late_days, total_working_days)
    
    return {
        "month": month,
        "year": year,
        "total_working_days": total_working_days,
        "present_days": present_days,
        "absent_days": absent_days,
        "late_days": late_days,
        "total_late_minutes": total_late_minutes,
        "total_penalty_amount": total_penalty,
        "attendance_percentage": round(attendance_percentage, 2),
        "punctuality_score": punctuality_score,
        "detailed_records": month_records
    }