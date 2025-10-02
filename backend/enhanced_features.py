from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import os
import base64

# Enhanced Models for new features

class EmployeeDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    document_type: str  # "Resume", "ID Proof", "Address Proof", "Educational Certificate", "Other"
    document_name: str
    file_path: str
    file_size: int
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: Optional[str] = ""

class CompanyAnnouncement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    announcement_type: str  # "General", "Policy", "Event", "Holiday", "Important"
    priority: str = "Medium"  # "Low", "Medium", "High", "Urgent"
    published_by: str
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: Optional[datetime] = None
    is_active: bool = True
    target_departments: List[str] = []  # Empty list means all departments

class DocumentUpload(BaseModel):
    employee_id: str
    document_type: str
    document_name: str
    description: str = ""

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    announcement_type: str
    priority: str = "Medium"
    valid_until: Optional[datetime] = None
    target_departments: List[str] = []

class EmployeeDocumentResponse(BaseModel):
    id: str
    employee_id: str
    document_type: str
    document_name: str
    file_size: int
    uploaded_by: str
    uploaded_at: datetime
    description: str

class AnnouncementResponse(BaseModel):
    id: str
    title: str
    content: str
    announcement_type: str
    priority: str
    published_by: str
    published_at: datetime
    valid_until: Optional[datetime]
    is_active: bool
    target_departments: List[str]

# File upload utilities
def save_uploaded_file(file: UploadFile, employee_id: str, document_type: str) -> tuple:
    """Save uploaded file and return file path and size"""
    # Create directory for employee documents
    upload_dir = f"/app/uploaded_documents/{employee_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{document_type}_{uuid.uuid4().hex[:8]}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
        file_size = len(content)
    
    return file_path, file_size

def get_file_as_base64(file_path: str) -> str:
    """Convert file to base64 for download"""
    try:
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

# Dashboard color scheme based on Vishwas World Tech logo
DASHBOARD_COLOR_SCHEME = {
    "primary": "#1E40AF",      # Deep Blue (logo primary)
    "secondary": "#3B82F6",    # Medium Blue  
    "accent": "#60A5FA",       # Light Blue
    "success": "#059669",      # Green for positive actions
    "warning": "#D97706",      # Orange for warnings
    "danger": "#DC2626",       # Red for alerts/delete
    "dark": "#1F2937",         # Dark gray for text
    "light": "#F8FAFC",        # Light background
    "gradient_start": "#1E3A8A", # Dark blue for gradients
    "gradient_end": "#3B82F6"    # Medium blue for gradients
}

def get_dashboard_theme():
    """Get dashboard theme configuration"""
    return {
        "company_branding": {
            "company_name": "Vishwas World Tech",
            "logo_url": "/assets/logo.png",
            "tagline": "Innovative Technology Solutions",
            "brand_colors": {
                "primary": "#1E40AF",
                "secondary": "#3B82F6"
            }
        },
        "color_scheme": DASHBOARD_COLOR_SCHEME,
        "design_elements": {
            "typography": {
                "primary_font": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
                "heading_font": "Poppins, sans-serif",
                "mono_font": "JetBrains Mono, monospace"
            },
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem", 
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "2rem",
                "2xl": "3rem"
            },
            "shadows": {
                "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
                "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
            },
            "border_radius": {
                "sm": "0.25rem",
                "md": "0.375rem",
                "lg": "0.5rem",
                "xl": "0.75rem"
            }
        }
    }

# Enhanced dashboard statistics
def get_enhanced_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    return {
        "employee_stats": {
            "total_employees": "Total workforce count",
            "active_employees": "Currently active employees",
            "on_leave": "Employees on leave today",
            "new_joiners_month": "New hires this month"
        },
        "attendance_stats": {
            "present_today": "Present employees today",
            "logged_in_now": "Currently online",
            "late_arrivals": "Late arrivals today",
            "early_departures": "Early departures today"
        },
        "document_stats": {
            "pending_documents": "Documents pending upload",
            "total_documents": "Total documents in system",
            "recent_uploads": "Documents uploaded this week"
        },
        "announcement_stats": {
            "active_announcements": "Active announcements",
            "recent_announcements": "Posted this week",
            "urgent_announcements": "Urgent announcements"
        }
    }