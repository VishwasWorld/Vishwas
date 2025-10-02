#!/usr/bin/env python3
"""
HRMS Backend API Testing Suite
Tests all backend APIs for the Vishwas World Tech HRMS system
"""

import requests
import json
from datetime import datetime, timezone
import uuid
import time

# Configuration
BASE_URL = "https://vishwas-hrms.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class HRMSAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "employees": {"passed": 0, "failed": 0, "details": []},
            "attendance": {"passed": 0, "failed": 0, "details": []},
            "dashboard": {"passed": 0, "failed": 0, "details": []},
            "documents": {"passed": 0, "failed": 0, "details": []},
            "salary": {"passed": 0, "failed": 0, "details": []},
            "employee_agreement": {"passed": 0, "failed": 0, "details": []},
            "company_policy": {"passed": 0, "failed": 0, "details": []}
        }
        self.created_employee_id = None
        
    def log_result(self, category, test_name, success, message, response_data=None):
        """Log test result"""
        if success:
            self.test_results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results[category]["failed"] += 1
            status = "❌ FAIL"
            
        detail = {
            "test": test_name,
            "status": status,
            "message": message,
            "response": response_data
        }
        self.test_results[category]["details"].append(detail)
        print(f"{status}: {test_name} - {message}")
        
    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n=== TESTING AUTHENTICATION SYSTEM ===")
        
        # Test 1: Valid login
        try:
            login_data = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            }
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "employee" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("authentication", "Admin Login", True, 
                                  f"Successfully logged in as {data['employee']['full_name']}")
                else:
                    self.log_result("authentication", "Admin Login", False, 
                                  "Response missing required fields", data)
            else:
                self.log_result("authentication", "Admin Login", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("authentication", "Admin Login", False, f"Exception: {str(e)}")
            
        # Test 2: Invalid credentials
        try:
            invalid_data = {
                "username": "invalid_user",
                "password": "wrong_password"
            }
            response = requests.post(f"{self.base_url}/auth/login", json=invalid_data)
            
            if response.status_code == 401:
                self.log_result("authentication", "Invalid Login", True, 
                              "Correctly rejected invalid credentials")
            else:
                self.log_result("authentication", "Invalid Login", False, 
                              f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("authentication", "Invalid Login", False, f"Exception: {str(e)}")
            
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    def test_employee_management(self):
        """Test employee management endpoints"""
        print("\n=== TESTING EMPLOYEE MANAGEMENT API ===")
        
        if not self.auth_token:
            self.log_result("employees", "Employee Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: Get all employees
        try:
            response = requests.get(f"{self.base_url}/employees", headers=headers)
            
            if response.status_code == 200:
                employees = response.json()
                if isinstance(employees, list):
                    self.log_result("employees", "Get All Employees", True, 
                                  f"Retrieved {len(employees)} employees")
                else:
                    self.log_result("employees", "Get All Employees", False, 
                                  "Response is not a list")
            else:
                self.log_result("employees", "Get All Employees", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("employees", "Get All Employees", False, f"Exception: {str(e)}")
            
        # Test 2: Create new employee
        try:
            new_employee_id = f"EMP{int(time.time())}"
            self.created_employee_id = new_employee_id
            
            employee_data = {
                "employee_id": new_employee_id,
                "full_name": "Rajesh Kumar",
                "department": "Software Development",
                "designation": "Senior Developer",
                "join_date": "2024-01-15T00:00:00Z",
                "manager": "Tech Lead",
                "contact_number": "+91-9876543210",
                "email_address": "rajesh.kumar@vishwasworld.com",
                "address": "123 Tech Park, Bangalore, Karnataka",
                "basic_salary": 75000.0,
                "username": f"rajesh_{int(time.time())}",
                "password": "rajesh123"
            }
            
            response = requests.post(f"{self.base_url}/employees", json=employee_data, headers=headers)
            
            if response.status_code == 200:
                created_employee = response.json()
                if created_employee.get("employee_id") == new_employee_id:
                    self.log_result("employees", "Create Employee", True, 
                                  f"Successfully created employee {created_employee['full_name']}")
                else:
                    self.log_result("employees", "Create Employee", False, 
                                  "Created employee data mismatch")
            else:
                self.log_result("employees", "Create Employee", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("employees", "Create Employee", False, f"Exception: {str(e)}")
            
        # Test 3: Get specific employee
        if self.created_employee_id:
            try:
                response = requests.get(f"{self.base_url}/employees/{self.created_employee_id}", 
                                      headers=headers)
                
                if response.status_code == 200:
                    employee = response.json()
                    if employee.get("employee_id") == self.created_employee_id:
                        self.log_result("employees", "Get Specific Employee", True, 
                                      f"Retrieved employee {employee['full_name']}")
                    else:
                        self.log_result("employees", "Get Specific Employee", False, 
                                      "Employee data mismatch")
                else:
                    self.log_result("employees", "Get Specific Employee", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result("employees", "Get Specific Employee", False, f"Exception: {str(e)}")
                
        # Test 4: Test authentication requirement
        try:
            response = requests.get(f"{self.base_url}/employees")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("employees", "Auth Required", True, 
                              "Correctly requires authentication")
            else:
                self.log_result("employees", "Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("employees", "Auth Required", False, f"Exception: {str(e)}")
            
    def test_attendance_tracking(self):
        """Test attendance tracking endpoints"""
        print("\n=== TESTING ATTENDANCE TRACKING API ===")
        
        if not self.auth_token:
            self.log_result("attendance", "Attendance Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Use admin employee ID for testing
        test_employee_id = "VWT001"  # Admin employee ID from database
        
        # Test 1: Employee login
        try:
            login_data = {
                "employee_id": test_employee_id,
                "location": {
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "address": "Vishwas World Tech Office, Bangalore"
                }
            }
            
            response = requests.post(f"{self.base_url}/attendance/login", 
                                   json=login_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "login_time" in data:
                    self.log_result("attendance", "Employee Login", True, 
                                  f"Successfully recorded login at {data['login_time']}")
                else:
                    self.log_result("attendance", "Employee Login", False, 
                                  "Response missing login_time")
            else:
                self.log_result("attendance", "Employee Login", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("attendance", "Employee Login", False, f"Exception: {str(e)}")
            
        # Wait a moment before logout
        time.sleep(2)
        
        # Test 2: Employee logout
        try:
            logout_data = {
                "employee_id": test_employee_id,
                "location": {
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "address": "Vishwas World Tech Office, Bangalore"
                }
            }
            
            response = requests.post(f"{self.base_url}/attendance/logout", 
                                   json=logout_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "total_hours" in data:
                    self.log_result("attendance", "Employee Logout", True, 
                                  f"Successfully recorded logout, total hours: {data['total_hours']}")
                else:
                    self.log_result("attendance", "Employee Logout", False, 
                                  "Response missing total_hours")
            else:
                self.log_result("attendance", "Employee Logout", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("attendance", "Employee Logout", False, f"Exception: {str(e)}")
            
        # Test 3: Get today's attendance
        try:
            response = requests.get(f"{self.base_url}/attendance/today", headers=headers)
            
            if response.status_code == 200:
                attendance_records = response.json()
                if isinstance(attendance_records, list):
                    self.log_result("attendance", "Today's Attendance", True, 
                                  f"Retrieved {len(attendance_records)} attendance records")
                else:
                    self.log_result("attendance", "Today's Attendance", False, 
                                  "Response is not a list")
            else:
                self.log_result("attendance", "Today's Attendance", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("attendance", "Today's Attendance", False, f"Exception: {str(e)}")
            
        # Test 4: Get employee attendance history
        try:
            response = requests.get(f"{self.base_url}/attendance/employee/{test_employee_id}", 
                                  headers=headers)
            
            if response.status_code == 200:
                attendance_history = response.json()
                if isinstance(attendance_history, list):
                    self.log_result("attendance", "Employee Attendance History", True, 
                                  f"Retrieved {len(attendance_history)} attendance records for employee")
                else:
                    self.log_result("attendance", "Employee Attendance History", False, 
                                  "Response is not a list")
            else:
                self.log_result("attendance", "Employee Attendance History", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("attendance", "Employee Attendance History", False, f"Exception: {str(e)}")
            
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        print("\n=== TESTING DASHBOARD STATISTICS API ===")
        
        if not self.auth_token:
            self.log_result("dashboard", "Dashboard Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test: Get dashboard statistics
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["total_employees", "present_today", "logged_in_now", "absent_today"]
                
                if all(field in stats for field in required_fields):
                    self.log_result("dashboard", "Dashboard Statistics", True, 
                                  f"Stats: {stats['total_employees']} total, {stats['present_today']} present, "
                                  f"{stats['logged_in_now']} logged in, {stats['absent_today']} absent")
                else:
                    missing_fields = [field for field in required_fields if field not in stats]
                    self.log_result("dashboard", "Dashboard Statistics", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("dashboard", "Dashboard Statistics", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("dashboard", "Dashboard Statistics", False, f"Exception: {str(e)}")
            
    def test_document_generation(self):
        """Test document generation endpoints"""
        print("\n=== TESTING DOCUMENT GENERATION API ===")
        
        if not self.auth_token:
            self.log_result("documents", "Document Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Use admin employee ID for testing
        test_employee_id = "VWT001"  # Admin employee ID from database
        
        # Test 1: Generate offer letter for admin user
        try:
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/generate-offer-letter", 
                                   headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["message", "document_type", "employee_id", "employee_name", "pdf_data", "filename"]
                
                if all(field in data for field in required_fields):
                    # Verify document type
                    if data["document_type"] == "offer_letter":
                        # Verify PDF data is base64 encoded
                        try:
                            import base64
                            base64.b64decode(data["pdf_data"])
                            pdf_valid = True
                        except:
                            pdf_valid = False
                            
                        if pdf_valid and data["employee_id"] == test_employee_id:
                            self.log_result("documents", "Generate Offer Letter", True, 
                                          f"Successfully generated offer letter for {data['employee_name']}, "
                                          f"filename: {data['filename']}, PDF size: {len(data['pdf_data'])} chars")
                        else:
                            self.log_result("documents", "Generate Offer Letter", False, 
                                          f"Invalid PDF data or employee ID mismatch")
                    else:
                        self.log_result("documents", "Generate Offer Letter", False, 
                                      f"Wrong document type: {data['document_type']}")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("documents", "Generate Offer Letter", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("documents", "Generate Offer Letter", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("documents", "Generate Offer Letter", False, f"Exception: {str(e)}")
            
        # Test 2: Generate appointment letter for admin user
        try:
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/generate-appointment-letter", 
                                   headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["message", "document_type", "employee_id", "employee_name", "pdf_data", "filename"]
                
                if all(field in data for field in required_fields):
                    # Verify document type
                    if data["document_type"] == "appointment_letter":
                        # Verify PDF data is base64 encoded
                        try:
                            import base64
                            base64.b64decode(data["pdf_data"])
                            pdf_valid = True
                        except:
                            pdf_valid = False
                            
                        if pdf_valid and data["employee_id"] == test_employee_id:
                            self.log_result("documents", "Generate Appointment Letter", True, 
                                          f"Successfully generated appointment letter for {data['employee_name']}, "
                                          f"filename: {data['filename']}, PDF size: {len(data['pdf_data'])} chars")
                        else:
                            self.log_result("documents", "Generate Appointment Letter", False, 
                                          f"Invalid PDF data or employee ID mismatch")
                    else:
                        self.log_result("documents", "Generate Appointment Letter", False, 
                                      f"Wrong document type: {data['document_type']}")
                else:
                    missing_fields = [field for field in required_fields if field not in required_fields]
                    self.log_result("documents", "Generate Appointment Letter", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("documents", "Generate Appointment Letter", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("documents", "Generate Appointment Letter", False, f"Exception: {str(e)}")
            
        # Test 3: Test with invalid employee ID
        try:
            invalid_employee_id = "INVALID123"
            response = requests.post(f"{self.base_url}/employees/{invalid_employee_id}/generate-offer-letter", 
                                   headers=headers)
            
            if response.status_code == 404:
                self.log_result("documents", "Invalid Employee ID Error Handling", True, 
                              "Correctly returned 404 for invalid employee ID")
            else:
                self.log_result("documents", "Invalid Employee ID Error Handling", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("documents", "Invalid Employee ID Error Handling", False, f"Exception: {str(e)}")
            
        # Test 4: Test authentication requirement for document endpoints
        try:
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/generate-offer-letter")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("documents", "Document Auth Required", True, 
                              "Correctly requires authentication for document generation")
            else:
                self.log_result("documents", "Document Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("documents", "Document Auth Required", False, f"Exception: {str(e)}")
            
        # Test 5: Verify document content includes company letterhead (by checking PDF size and structure)
        try:
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/generate-offer-letter", 
                                   headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                pdf_data = data.get("pdf_data", "")
                
                # A proper PDF with letterhead should be reasonably sized (>3KB base64)
                if len(pdf_data) > 3000:  # Base64 encoded PDF should be substantial
                    # Check filename contains company/employee info
                    filename = data.get("filename", "")
                    if "Offer_Letter" in filename and test_employee_id in filename:
                        self.log_result("documents", "Document Content Verification", True, 
                                      f"Document appears to contain proper content, size: {len(pdf_data)} chars")
                    else:
                        self.log_result("documents", "Document Content Verification", False, 
                                      f"Filename format incorrect: {filename}")
                else:
                    self.log_result("documents", "Document Content Verification", False, 
                                  f"PDF appears too small, may be missing content: {len(pdf_data)} chars")
            else:
                self.log_result("documents", "Document Content Verification", False, 
                              f"Could not retrieve document for content verification")
                
        except Exception as e:
            self.log_result("documents", "Document Content Verification", False, f"Exception: {str(e)}")
            
    def test_salary_calculation(self):
        """Test salary calculation endpoints"""
        print("\n=== TESTING SALARY CALCULATION API ===")
        
        if not self.auth_token:
            self.log_result("salary", "Salary Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Use admin employee ID for testing
        test_employee_id = "VWT001"  # Admin employee ID from database
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Test 1: Get salary rates
        try:
            response = requests.get(f"{self.base_url}/salary/rates", headers=headers)
            
            if response.status_code == 200:
                rates = response.json()
                required_sections = ["government_rates", "allowance_rates"]
                
                if all(section in rates for section in required_sections):
                    # Check government rates structure
                    gov_rates = rates["government_rates"]
                    if all(key in gov_rates for key in ["esi", "pf", "professional_tax"]):
                        # Verify ESI rate
                        esi_rate = gov_rates["esi"]["rate"]
                        esi_limit = gov_rates["esi"]["wage_limit"]
                        if esi_rate == "1.75%" and esi_limit == 21000:
                            self.log_result("salary", "Get Salary Rates", True, 
                                          f"Successfully retrieved government rates - ESI: {esi_rate}, PF: {gov_rates['pf']['employee_rate']}, PT: Karnataka rates")
                        else:
                            self.log_result("salary", "Get Salary Rates", False, 
                                          f"Incorrect ESI rates - Expected 1.75% and ₹21,000 limit, got {esi_rate} and ₹{esi_limit}")
                    else:
                        self.log_result("salary", "Get Salary Rates", False, 
                                      "Missing required government rate sections")
                else:
                    self.log_result("salary", "Get Salary Rates", False, 
                                  f"Missing required sections: {[s for s in required_sections if s not in rates]}")
            else:
                self.log_result("salary", "Get Salary Rates", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("salary", "Get Salary Rates", False, f"Exception: {str(e)}")
            
        # Test 2: Get working days for current month
        try:
            response = requests.get(f"{self.base_url}/salary/working-days/{current_year}/{current_month}", 
                                  headers=headers)
            
            if response.status_code == 200:
                working_days_data = response.json()
                required_fields = ["year", "month", "working_days", "month_name"]
                
                if all(field in working_days_data for field in required_fields):
                    working_days = working_days_data["working_days"]
                    if isinstance(working_days, int) and working_days > 0:
                        self.log_result("salary", "Get Working Days", True, 
                                      f"Working days for {working_days_data['month_name']} {current_year}: {working_days} days")
                    else:
                        self.log_result("salary", "Get Working Days", False, 
                                      f"Invalid working days count: {working_days}")
                else:
                    missing_fields = [field for field in required_fields if field not in working_days_data]
                    self.log_result("salary", "Get Working Days", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("salary", "Get Working Days", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("salary", "Get Working Days", False, f"Exception: {str(e)}")
            
        # Test 3: Get employee attendance summary
        try:
            response = requests.get(f"{self.base_url}/employees/{test_employee_id}/attendance-summary/{current_year}/{current_month}", 
                                  headers=headers)
            
            if response.status_code == 200:
                attendance_summary = response.json()
                required_fields = ["employee_id", "year", "month", "present_days", "total_working_days", "attendance_percentage"]
                
                if all(field in attendance_summary for field in required_fields):
                    present_days = attendance_summary["present_days"]
                    total_days = attendance_summary["total_working_days"]
                    attendance_pct = attendance_summary["attendance_percentage"]
                    
                    if attendance_summary["employee_id"] == test_employee_id:
                        self.log_result("salary", "Get Attendance Summary", True, 
                                      f"Attendance summary for {test_employee_id}: {present_days}/{total_days} days ({attendance_pct}%)")
                    else:
                        self.log_result("salary", "Get Attendance Summary", False, 
                                      f"Employee ID mismatch: expected {test_employee_id}, got {attendance_summary['employee_id']}")
                else:
                    missing_fields = [field for field in required_fields if field not in attendance_summary]
                    self.log_result("salary", "Get Attendance Summary", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("salary", "Get Attendance Summary", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("salary", "Get Attendance Summary", False, f"Exception: {str(e)}")
            
        # Test 4: Calculate salary for admin user
        try:
            salary_request = {
                "employee_id": test_employee_id,
                "year": current_year,
                "month": current_month
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/calculate-salary", 
                                   json=salary_request, headers=headers)
            
            if response.status_code == 200:
                salary_data = response.json()
                
                if "calculation" in salary_data:
                    calculation = salary_data["calculation"]
                    required_sections = ["employee_info", "earnings", "deductions", "net_salary"]
                    
                    if all(section in calculation for section in required_sections):
                        earnings = calculation["earnings"]
                        deductions = calculation["deductions"]
                        net_salary = calculation["net_salary"]
                        
                        # Verify expected calculations for admin user (basic salary ₹50,000)
                        basic_salary = earnings.get("basic_salary", 0)
                        hra = earnings.get("hra", 0)
                        da = earnings.get("da", 0)
                        gross_salary = earnings.get("gross_salary", 0)
                        pf_deduction = deductions.get("pf_employee", 0)
                        esi_deduction = deductions.get("esi_employee", 0)
                        pt_deduction = deductions.get("professional_tax", 0)
                        
                        # Verify calculations
                        calculation_errors = []
                        
                        # Check if basic salary is around ₹50,000 (may be pro-rated)
                        if basic_salary <= 0:
                            calculation_errors.append("Basic salary is zero or negative")
                            
                        # Check HRA (40% of basic for non-metro)
                        expected_hra = basic_salary * 0.40
                        if abs(hra - expected_hra) > 1:  # Allow ₹1 rounding difference
                            calculation_errors.append(f"HRA calculation incorrect: expected ~₹{expected_hra:.2f}, got ₹{hra}")
                            
                        # Check DA (10% of basic)
                        expected_da = basic_salary * 0.10
                        if abs(da - expected_da) > 1:
                            calculation_errors.append(f"DA calculation incorrect: expected ~₹{expected_da:.2f}, got ₹{da}")
                            
                        # Check PF (12% of basic, max ₹15,000)
                        expected_pf = min(basic_salary, 15000) * 0.12
                        if abs(pf_deduction - expected_pf) > 1:
                            calculation_errors.append(f"PF calculation incorrect: expected ~₹{expected_pf:.2f}, got ₹{pf_deduction}")
                            
                        # Check ESI (should be 0 if gross > ₹21,000)
                        if gross_salary > 21000 and esi_deduction > 0:
                            calculation_errors.append(f"ESI should be 0 for gross salary > ₹21,000, but got ₹{esi_deduction}")
                        elif gross_salary <= 21000:
                            expected_esi = gross_salary * 0.0175
                            if abs(esi_deduction - expected_esi) > 1:
                                calculation_errors.append(f"ESI calculation incorrect: expected ~₹{expected_esi:.2f}, got ₹{esi_deduction}")
                                
                        # Check Professional Tax (₹200 for Karnataka if salary > ₹25,000)
                        if gross_salary > 25000 and pt_deduction != 200:
                            calculation_errors.append(f"Professional Tax should be ₹200 for salary > ₹25,000, got ₹{pt_deduction}")
                        elif gross_salary <= 25000 and gross_salary > 15000 and pt_deduction != 200:
                            calculation_errors.append(f"Professional Tax should be ₹200 for salary ₹15,001-₹25,000, got ₹{pt_deduction}")
                            
                        if not calculation_errors:
                            self.log_result("salary", "Calculate Employee Salary", True, 
                                          f"Salary calculated correctly - Basic: ₹{basic_salary:.2f}, HRA: ₹{hra:.2f}, "
                                          f"DA: ₹{da:.2f}, Gross: ₹{gross_salary:.2f}, PF: ₹{pf_deduction:.2f}, "
                                          f"ESI: ₹{esi_deduction:.2f}, PT: ₹{pt_deduction:.2f}, Net: ₹{net_salary:.2f}")
                        else:
                            self.log_result("salary", "Calculate Employee Salary", False, 
                                          f"Salary calculation errors: {'; '.join(calculation_errors)}")
                    else:
                        missing_sections = [section for section in required_sections if section not in calculation]
                        self.log_result("salary", "Calculate Employee Salary", False, 
                                      f"Missing calculation sections: {missing_sections}")
                else:
                    self.log_result("salary", "Calculate Employee Salary", False, 
                                  "Response missing 'calculation' field")
            else:
                self.log_result("salary", "Calculate Employee Salary", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("salary", "Calculate Employee Salary", False, f"Exception: {str(e)}")
            
        # Test 5: Generate salary slip PDF
        try:
            salary_request = {
                "employee_id": test_employee_id,
                "year": current_year,
                "month": current_month
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/generate-salary-slip", 
                                   json=salary_request, headers=headers)
            
            if response.status_code == 200:
                slip_data = response.json()
                required_fields = ["message", "employee_id", "employee_name", "month_year", "pdf_data", "filename"]
                
                if all(field in slip_data for field in required_fields):
                    # Verify PDF data is base64 encoded
                    try:
                        import base64
                        base64.b64decode(slip_data["pdf_data"])
                        pdf_valid = True
                    except:
                        pdf_valid = False
                        
                    if pdf_valid and slip_data["employee_id"] == test_employee_id:
                        # Check if PDF is substantial (should contain salary breakdown)
                        pdf_size = len(slip_data["pdf_data"])
                        if pdf_size > 5000:  # Base64 encoded PDF should be substantial
                            self.log_result("salary", "Generate Salary Slip", True, 
                                          f"Successfully generated salary slip for {slip_data['employee_name']}, "
                                          f"month: {slip_data['month_year']}, PDF size: {pdf_size} chars")
                        else:
                            self.log_result("salary", "Generate Salary Slip", False, 
                                          f"PDF appears too small: {pdf_size} chars")
                    else:
                        self.log_result("salary", "Generate Salary Slip", False, 
                                      f"Invalid PDF data or employee ID mismatch")
                else:
                    missing_fields = [field for field in required_fields if field not in slip_data]
                    self.log_result("salary", "Generate Salary Slip", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("salary", "Generate Salary Slip", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("salary", "Generate Salary Slip", False, f"Exception: {str(e)}")
            
        # Test 6: Test authentication requirement for salary endpoints
        try:
            response = requests.get(f"{self.base_url}/salary/rates")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("salary", "Salary Auth Required", True, 
                              "Correctly requires authentication for salary endpoints")
            else:
                self.log_result("salary", "Salary Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("salary", "Salary Auth Required", False, f"Exception: {str(e)}")
            
        # Test 7: Test with invalid employee ID
        try:
            invalid_employee_id = "INVALID123"
            salary_request = {
                "employee_id": invalid_employee_id,
                "year": current_year,
                "month": current_month
            }
            
            response = requests.post(f"{self.base_url}/employees/{invalid_employee_id}/calculate-salary", 
                                   json=salary_request, headers=headers)
            
            if response.status_code == 404:
                self.log_result("salary", "Invalid Employee Salary Calculation", True, 
                              "Correctly returned 404 for invalid employee ID")
            else:
                self.log_result("salary", "Invalid Employee Salary Calculation", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("salary", "Invalid Employee Salary Calculation", False, f"Exception: {str(e)}")
            
        # Test 8: Test different months (previous month)
        try:
            prev_month = current_month - 1 if current_month > 1 else 12
            prev_year = current_year if current_month > 1 else current_year - 1
            
            response = requests.get(f"{self.base_url}/salary/working-days/{prev_year}/{prev_month}", 
                                  headers=headers)
            
            if response.status_code == 200:
                working_days_data = response.json()
                if working_days_data.get("working_days", 0) > 0:
                    self.log_result("salary", "Different Month Working Days", True, 
                                  f"Working days for {working_days_data.get('month_name', 'Unknown')} {prev_year}: {working_days_data['working_days']} days")
                else:
                    self.log_result("salary", "Different Month Working Days", False, 
                                  "Invalid working days for previous month")
            else:
                self.log_result("salary", "Different Month Working Days", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("salary", "Different Month Working Days", False, f"Exception: {str(e)}")
            
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting HRMS Backend API Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run tests in order
        self.test_authentication()
        self.test_employee_management()
        self.test_attendance_tracking()
        self.test_dashboard_stats()
        self.test_document_generation()
        self.test_salary_calculation()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🧪 TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status_icon = "✅" if failed == 0 else "❌"
            print(f"{status_icon} {category.upper()}: {passed} passed, {failed} failed")
            
            # Show failed tests
            if failed > 0:
                for detail in results["details"]:
                    if "❌" in detail["status"]:
                        print(f"   - {detail['test']}: {detail['message']}")
                        
        print("-" * 60)
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"❌ {total_failed} TESTS FAILED"
        print(f"OVERALL: {total_passed} passed, {total_failed} failed - {overall_status}")
        print("=" * 60)
        
        return total_failed == 0

if __name__ == "__main__":
    tester = HRMSAPITester()
    success = tester.run_all_tests()
    
    if not success:
        exit(1)