from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone, date
import uuid

# Interview Scheduling Models
class InterviewCandidate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_name: str
    email: str
    phone: str
    position_applied: str
    department: str
    experience_years: float
    resume_path: str = ""
    interview_date: datetime
    interview_time: str  # HH:MM format
    interview_type: str  # "Technical", "HR", "Managerial", "Final"
    interviewer_name: str
    interview_mode: str  # "Online", "Offline", "Hybrid"
    interview_status: str = "Scheduled"  # "Scheduled", "Completed", "Cancelled", "Rescheduled"
    interview_location: str = ""
    interview_notes: str = ""
    candidate_status: str = "Active"  # "Active", "Selected", "Rejected", "On Hold"
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InterviewCandidateCreate(BaseModel):
    candidate_name: str
    email: str
    phone: str
    position_applied: str
    department: str
    experience_years: float
    interview_date: datetime
    interview_time: str
    interview_type: str
    interviewer_name: str
    interview_mode: str
    interview_location: str = ""
    interview_notes: str = ""

class InterviewCandidateResponse(BaseModel):
    id: str
    candidate_name: str
    email: str
    phone: str
    position_applied: str
    department: str
    experience_years: float
    interview_date: datetime
    interview_time: str
    interview_type: str
    interviewer_name: str
    interview_mode: str
    interview_status: str
    interview_location: str
    candidate_status: str
    created_at: datetime

# Working Employee Models (Enhanced Employee Model)
class WorkingEmployeeStatus(BaseModel):
    current_project: str = ""
    project_start_date: Optional[date] = None
    project_end_date: Optional[date] = None
    performance_rating: str = "Good"  # "Excellent", "Good", "Average", "Needs Improvement"
    last_appraisal_date: Optional[date] = None
    next_appraisal_date: Optional[date] = None
    training_status: str = "Up to Date"  # "Up to Date", "Pending", "In Progress"
    work_location: str = "Office"  # "Office", "Remote", "Hybrid"
    shift_timing: str = "9:45 AM - 6:45 PM"
    reporting_manager: str = ""
    team_members: List[str] = []

class WorkingEmployee(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    full_name: str
    department: str
    designation: str
    join_date: datetime
    email_address: str
    contact_number: str
    basic_salary: float
    employee_status: WorkingEmployeeStatus
    emergency_contact: dict = {}
    bank_details: dict = {}
    last_login: Optional[datetime] = None
    total_experience: str = ""
    skills: List[str] = []
    certifications: List[str] = []

# Holiday Calendar Models
class CompanyHoliday(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    holiday_name: str
    holiday_date: date
    holiday_type: str  # "National", "Regional", "Company", "Optional"
    description: str = ""
    is_mandatory: bool = True
    applicable_locations: List[str] = ["All"]
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CompanyHolidayCreate(BaseModel):
    holiday_name: str
    holiday_date: date
    holiday_type: str
    description: str = ""
    is_mandatory: bool = True
    applicable_locations: List[str] = ["All"]

class CompanyHolidayResponse(BaseModel):
    id: str
    holiday_name: str
    holiday_date: date
    holiday_type: str
    description: str
    is_mandatory: bool
    applicable_locations: List[str]
    created_at: datetime

class HolidayCalendarYear(BaseModel):
    year: int
    holidays: List[CompanyHolidayResponse]
    total_holidays: int
    mandatory_holidays: int
    optional_holidays: int

# Employee Database Models (Enhanced)
class EmployeeDatabase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    full_name: str
    department: str
    designation: str
    join_date: datetime
    email_address: str
    contact_number: str
    address: str
    basic_salary: float
    status: str = "Active"  # "Active", "Inactive", "On Leave", "Terminated"
    employee_type: str = "Full Time"  # "Full Time", "Part Time", "Contract", "Intern"
    qualification: str = ""
    previous_experience: str = ""
    date_of_birth: Optional[date] = None
    gender: str = ""
    marital_status: str = ""
    blood_group: str = ""
    aadhar_number: str = ""
    pan_number: str = ""
    passport_number: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Dashboard Statistics Models
class DashboardStats(BaseModel):
    employee_database: dict
    interview_candidates: dict
    working_employees: dict
    announcements: dict
    holidays: dict
    system_overview: dict

# Department and Position Masters
DEPARTMENTS = [
    "Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", 
    "Support", "Quality Assurance", "Product Management", "Design",
    "Business Development", "Administration", "Legal", "Research"
]

DESIGNATIONS = {
    "Engineering": ["Software Engineer", "Senior Software Engineer", "Tech Lead", "Engineering Manager", "CTO"],
    "Sales": ["Sales Executive", "Senior Sales Executive", "Sales Manager", "Regional Sales Manager", "VP Sales"],
    "Marketing": ["Marketing Executive", "Digital Marketing Specialist", "Marketing Manager", "Brand Manager", "CMO"],
    "HR": ["HR Executive", "Senior HR Executive", "HR Manager", "HR Business Partner", "CHRO"],
    "Finance": ["Accounts Executive", "Financial Analyst", "Finance Manager", "Controller", "CFO"],
    "Operations": ["Operations Executive", "Operations Manager", "Process Manager", "Operations Head", "COO"],
    "Support": ["Support Executive", "Support Lead", "Support Manager", "Customer Success Manager"],
    "Quality Assurance": ["QA Engineer", "Senior QA Engineer", "QA Lead", "QA Manager", "Head of Quality"],
    "Product Management": ["Product Executive", "Product Manager", "Senior Product Manager", "VP Product"],
    "Design": ["UI Designer", "UX Designer", "Senior Designer", "Design Lead", "Head of Design"]
}

INTERVIEW_TYPES = ["Screening", "Technical", "HR", "Managerial", "Final Round", "Panel Interview"]

HOLIDAY_TYPES = ["National Holiday", "Regional Holiday", "Company Holiday", "Optional Holiday", "Festival"]

def get_indian_national_holidays(year: int) -> List[dict]:
    """Get standard Indian national holidays for a year"""
    holidays = [
        {"name": "New Year's Day", "date": f"{year}-01-01", "type": "National"},
        {"name": "Republic Day", "date": f"{year}-01-26", "type": "National"},
        {"name": "Independence Day", "date": f"{year}-08-15", "type": "National"},
        {"name": "Gandhi Jayanti", "date": f"{year}-10-02", "type": "National"},
        {"name": "Diwali", "date": f"{year}-11-12", "type": "National"},  # Approximate
        {"name": "Christmas Day", "date": f"{year}-12-25", "type": "National"},
        {"name": "Good Friday", "date": f"{year}-04-18", "type": "National"},  # Approximate
        {"name": "Holi", "date": f"{year}-03-13", "type": "National"},  # Approximate
        {"name": "Eid ul-Fitr", "date": f"{year}-04-21", "type": "National"},  # Approximate
        {"name": "Dussehra", "date": f"{year}-10-24", "type": "National"},  # Approximate
    ]
    
    # Add Bangalore specific holidays
    bangalore_holidays = [
        {"name": "Karnataka Rajyotsava", "date": f"{year}-11-01", "type": "Regional"},
        {"name": "Ugadi", "date": f"{year}-04-09", "type": "Regional"},
        {"name": "Gowri Ganesha", "date": f"{year}-09-07", "type": "Regional"},
    ]
    
    return holidays + bangalore_holidays

def get_dashboard_overview():
    """Get dashboard overview configuration"""
    return {
        "modules": [
            {
                "id": "employee_database",
                "name": "Employee Database",
                "description": "Complete employee records and information",
                "icon": "👥",
                "color": "blue"
            },
            {
                "id": "interview_scheduled",
                "name": "Interview Scheduled",
                "description": "Manage candidate interviews and scheduling",
                "icon": "📅",
                "color": "green"
            },
            {
                "id": "working_employee",
                "name": "Working Employee Database",
                "description": "Active employee management and tracking",
                "icon": "💼",
                "color": "purple"
            },
            {
                "id": "announcements",
                "name": "Announcements",
                "description": "Company announcements and communications",
                "icon": "📢",
                "color": "orange"
            },
            {
                "id": "holiday_calendar",
                "name": "Yearly Holiday Calendar",
                "description": "Company holidays and leave calendar",
                "icon": "📆",
                "color": "red"
            }
        ],
        "quick_actions": [
            "Add New Employee",
            "Schedule Interview",
            "Create Announcement",
            "Add Holiday",
            "Generate Reports"
        ]
    }