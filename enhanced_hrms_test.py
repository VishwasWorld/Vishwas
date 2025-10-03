#!/usr/bin/env python3
"""
Enhanced HRMS Backend API Testing Suite
Tests the new enhanced HRMS backend functionality including:
- Interview Scheduling System
- Working Employee Database
- Holiday Calendar Management
- Digital Salary Slip with Signatures
- Multi-channel Salary Sharing
- Enhanced Dashboard
"""

import requests
import json
from datetime import datetime, timezone, timedelta
import uuid
import time

# Configuration
BASE_URL = "https://vishwashrms.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class EnhancedHRMSTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "interviews": {"passed": 0, "failed": 0, "details": []},
            "working_employees": {"passed": 0, "failed": 0, "details": []},
            "holidays": {"passed": 0, "failed": 0, "details": []},
            "digital_salary": {"passed": 0, "failed": 0, "details": []},
            "multi_channel": {"passed": 0, "failed": 0, "details": []},
            "enhanced_dashboard": {"passed": 0, "failed": 0, "details": []}
        }
        self.created_interview_id = None
        self.created_holiday_id = None
        
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
        
    def authenticate(self):
        """Authenticate and get JWT token"""
        print("\n=== AUTHENTICATING FOR ENHANCED HRMS TESTING ===")
        
        try:
            login_data = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            }
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("authentication", "Admin Authentication", True, 
                                  f"Successfully authenticated as {data['employee']['full_name']}")
                    return True
                else:
                    self.log_result("authentication", "Admin Authentication", False, 
                                  "Response missing access_token", data)
                    return False
            else:
                self.log_result("authentication", "Admin Authentication", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("authentication", "Admin Authentication", False, f"Exception: {str(e)}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    def test_interview_scheduling_system(self):
        """Test Interview Scheduling System endpoints"""
        print("\n=== TESTING INTERVIEW SCHEDULING SYSTEM ===")
        
        if not self.auth_token:
            self.log_result("interviews", "Interview Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: Create new interview
        try:
            interview_data = {
                "candidate_name": "Priya Sharma",
                "email": "priya.sharma@email.com",
                "phone": "+91-9876543210",
                "position_applied": "Senior Software Engineer",
                "department": "Software Development",
                "interview_type": "Technical",
                "interview_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "interview_time": "10:00",
                "interviewer_name": "Tech Lead",
                "interview_mode": "In-person",
                "experience_years": 5,
                "interview_location": "Bangalore Office",
                "interview_notes": "Strong candidate with React and Node.js experience"
            }
            
            response = requests.post(f"{self.base_url}/interviews", json=interview_data, headers=headers)
            
            if response.status_code == 200:
                created_interview = response.json()
                required_fields = ["id", "candidate_name", "position", "interview_date", "interview_status"]
                
                if all(field in created_interview for field in required_fields):
                    self.created_interview_id = created_interview["id"]
                    self.log_result("interviews", "Create Interview", True, 
                                  f"Successfully created interview for {created_interview['candidate_name']} - {created_interview['position']}")
                else:
                    missing_fields = [field for field in required_fields if field not in created_interview]
                    self.log_result("interviews", "Create Interview", False, 
                                  f"Missing fields in response: {missing_fields}")
            else:
                self.log_result("interviews", "Create Interview", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("interviews", "Create Interview", False, f"Exception: {str(e)}")
            
        # Test 2: Get all interviews
        try:
            response = requests.get(f"{self.base_url}/interviews", headers=headers)
            
            if response.status_code == 200:
                interviews = response.json()
                if isinstance(interviews, list):
                    self.log_result("interviews", "Get All Interviews", True, 
                                  f"Retrieved {len(interviews)} scheduled interviews")
                else:
                    self.log_result("interviews", "Get All Interviews", False, 
                                  "Response is not a list")
            else:
                self.log_result("interviews", "Get All Interviews", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("interviews", "Get All Interviews", False, f"Exception: {str(e)}")
            
        # Test 3: Get interviews with status filter
        try:
            response = requests.get(f"{self.base_url}/interviews?status=Scheduled", headers=headers)
            
            if response.status_code == 200:
                scheduled_interviews = response.json()
                if isinstance(scheduled_interviews, list):
                    self.log_result("interviews", "Get Interviews by Status", True, 
                                  f"Retrieved {len(scheduled_interviews)} scheduled interviews")
                else:
                    self.log_result("interviews", "Get Interviews by Status", False, 
                                  "Response is not a list")
            else:
                self.log_result("interviews", "Get Interviews by Status", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("interviews", "Get Interviews by Status", False, f"Exception: {str(e)}")
            
        # Test 4: Update interview status
        if self.created_interview_id:
            try:
                update_data = {
                    "status": "Completed",
                    "notes": "Excellent technical skills, recommended for hiring"
                }
                
                response = requests.put(f"{self.base_url}/interviews/{self.created_interview_id}", 
                                      params=update_data, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    if "message" in result:
                        self.log_result("interviews", "Update Interview Status", True, 
                                      f"Successfully updated interview status to Completed")
                    else:
                        self.log_result("interviews", "Update Interview Status", False, 
                                      "Response missing success message")
                else:
                    self.log_result("interviews", "Update Interview Status", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result("interviews", "Update Interview Status", False, f"Exception: {str(e)}")
                
        # Test 5: Test authentication requirement
        try:
            response = requests.get(f"{self.base_url}/interviews")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("interviews", "Interview Auth Required", True, 
                              "Correctly requires authentication for interview endpoints")
            else:
                self.log_result("interviews", "Interview Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("interviews", "Interview Auth Required", False, f"Exception: {str(e)}")
            
    def test_working_employee_database(self):
        """Test Working Employee Database endpoints"""
        print("\n=== TESTING WORKING EMPLOYEE DATABASE ===")
        
        if not self.auth_token:
            self.log_result("working_employees", "Working Employee Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: Get all working employees
        try:
            response = requests.get(f"{self.base_url}/working-employees", headers=headers)
            
            if response.status_code == 200:
                employees = response.json()
                if isinstance(employees, list):
                    # Verify enhanced employee data structure
                    if employees:
                        first_employee = employees[0]
                        expected_fields = ["employee_id", "full_name", "department", "designation", 
                                         "document_completion", "total_documents", "last_login"]
                        
                        if all(field in first_employee for field in expected_fields):
                            self.log_result("working_employees", "Get Working Employees", True, 
                                          f"Retrieved {len(employees)} working employees with enhanced data")
                        else:
                            missing_fields = [field for field in expected_fields if field not in first_employee]
                            self.log_result("working_employees", "Get Working Employees", False, 
                                          f"Missing enhanced fields: {missing_fields}")
                    else:
                        self.log_result("working_employees", "Get Working Employees", True, 
                                      "Retrieved 0 working employees (empty database)")
                else:
                    self.log_result("working_employees", "Get Working Employees", False, 
                                  "Response is not a list")
            else:
                self.log_result("working_employees", "Get Working Employees", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("working_employees", "Get Working Employees", False, f"Exception: {str(e)}")
            
        # Test 2: Get working employees by department
        try:
            response = requests.get(f"{self.base_url}/working-employees?department=Software Development", 
                                  headers=headers)
            
            if response.status_code == 200:
                dept_employees = response.json()
                if isinstance(dept_employees, list):
                    self.log_result("working_employees", "Get Employees by Department", True, 
                                  f"Retrieved {len(dept_employees)} employees from Software Development")
                else:
                    self.log_result("working_employees", "Get Employees by Department", False, 
                                  "Response is not a list")
            else:
                self.log_result("working_employees", "Get Employees by Department", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("working_employees", "Get Employees by Department", False, f"Exception: {str(e)}")
            
        # Test 3: Get employee attendance report
        try:
            # Use admin employee ID for testing
            test_employee_id = "VWT001"
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            response = requests.get(f"{self.base_url}/working-employees/{test_employee_id}/attendance-report", 
                                  params={"month": current_month, "year": current_year}, headers=headers)
            
            if response.status_code == 200:
                report = response.json()
                expected_fields = ["employee_id", "month", "year", "attendance_summary", "working_hours_analysis"]
                
                if any(field in report for field in expected_fields):
                    self.log_result("working_employees", "Get Attendance Report", True, 
                                  f"Successfully generated attendance report for employee {test_employee_id}")
                else:
                    self.log_result("working_employees", "Get Attendance Report", False, 
                                  f"Report missing expected structure: {list(report.keys())}")
            else:
                self.log_result("working_employees", "Get Attendance Report", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("working_employees", "Get Attendance Report", False, f"Exception: {str(e)}")
            
        # Test 4: Test authentication requirement
        try:
            response = requests.get(f"{self.base_url}/working-employees")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("working_employees", "Working Employee Auth Required", True, 
                              "Correctly requires authentication for working employee endpoints")
            else:
                self.log_result("working_employees", "Working Employee Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("working_employees", "Working Employee Auth Required", False, f"Exception: {str(e)}")
            
    def test_holiday_calendar_management(self):
        """Test Holiday Calendar Management endpoints"""
        print("\n=== TESTING HOLIDAY CALENDAR MANAGEMENT ===")
        
        if not self.auth_token:
            self.log_result("holidays", "Holiday Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: Create company holiday
        try:
            from datetime import date
            holiday_data = {
                "holiday_name": "Company Foundation Day",
                "holiday_date": date(2025, 3, 15).isoformat(),
                "holiday_type": "Company",
                "description": "Celebrating 10 years of Vishwas World Tech",
                "is_mandatory": True,
                "applicable_locations": ["Bangalore", "All Offices"]
            }
            
            response = requests.post(f"{self.base_url}/holidays", json=holiday_data, headers=headers)
            
            if response.status_code == 200:
                created_holiday = response.json()
                required_fields = ["id", "holiday_name", "holiday_date", "holiday_type"]
                
                if all(field in created_holiday for field in required_fields):
                    self.created_holiday_id = created_holiday["id"]
                    self.log_result("holidays", "Create Company Holiday", True, 
                                  f"Successfully created holiday: {created_holiday['holiday_name']} on {created_holiday['holiday_date']}")
                else:
                    missing_fields = [field for field in required_fields if field not in created_holiday]
                    self.log_result("holidays", "Create Company Holiday", False, 
                                  f"Missing fields in response: {missing_fields}")
            else:
                self.log_result("holidays", "Create Company Holiday", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("holidays", "Create Company Holiday", False, f"Exception: {str(e)}")
            
        # Test 2: Get yearly holiday calendar (2025)
        try:
            response = requests.get(f"{self.base_url}/holidays/2025", headers=headers)
            
            if response.status_code == 200:
                calendar_data = response.json()
                required_fields = ["year", "holidays", "total_holidays", "mandatory_holidays", "optional_holidays"]
                
                if all(field in calendar_data for field in required_fields):
                    holidays = calendar_data["holidays"]
                    total_holidays = calendar_data["total_holidays"]
                    mandatory_count = calendar_data["mandatory_holidays"]
                    
                    if isinstance(holidays, list) and total_holidays > 0:
                        # Check if we have both national and company holidays
                        holiday_types = [h.get("holiday_type", "") for h in holidays]
                        has_national = any("National" in ht for ht in holiday_types)
                        has_company = any("Company" in ht for ht in holiday_types)
                        
                        self.log_result("holidays", "Get Yearly Holiday Calendar", True, 
                                      f"Retrieved 2025 calendar: {total_holidays} total holidays "
                                      f"({mandatory_count} mandatory), includes national: {has_national}, company: {has_company}")
                    else:
                        self.log_result("holidays", "Get Yearly Holiday Calendar", False, 
                                      f"Invalid holiday data structure or empty calendar")
                else:
                    missing_fields = [field for field in required_fields if field not in calendar_data]
                    self.log_result("holidays", "Get Yearly Holiday Calendar", False, 
                                  f"Missing fields in response: {missing_fields}")
            else:
                self.log_result("holidays", "Get Yearly Holiday Calendar", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("holidays", "Get Yearly Holiday Calendar", False, f"Exception: {str(e)}")
            
        # Test 3: Test with different year (2024)
        try:
            response = requests.get(f"{self.base_url}/holidays/2024", headers=headers)
            
            if response.status_code == 200:
                calendar_2024 = response.json()
                if calendar_2024.get("year") == 2024 and calendar_2024.get("total_holidays", 0) > 0:
                    self.log_result("holidays", "Get Different Year Calendar", True, 
                                  f"Retrieved 2024 calendar: {calendar_2024['total_holidays']} holidays")
                else:
                    self.log_result("holidays", "Get Different Year Calendar", False, 
                                  "Invalid 2024 calendar data")
            else:
                self.log_result("holidays", "Get Different Year Calendar", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("holidays", "Get Different Year Calendar", False, f"Exception: {str(e)}")
            
        # Test 4: Test authentication requirement
        try:
            response = requests.get(f"{self.base_url}/holidays/2025")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("holidays", "Holiday Auth Required", True, 
                              "Correctly requires authentication for holiday endpoints")
            else:
                self.log_result("holidays", "Holiday Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("holidays", "Holiday Auth Required", False, f"Exception: {str(e)}")
            
    def test_digital_salary_slip_with_signature(self):
        """Test Digital Salary Slip with QR Code Signature"""
        print("\n=== TESTING DIGITAL SALARY SLIP WITH SIGNATURE ===")
        
        if not self.auth_token:
            self.log_result("digital_salary", "Digital Salary Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Use admin employee ID for testing
        test_employee_id = "VWT001"
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Test 1: Generate digital salary slip with signature
        try:
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/generate-digital-salary-slip", 
                                   params={"month": current_month, "year": current_year}, headers=headers)
            
            if response.status_code == 200:
                slip_data = response.json()
                required_fields = ["message", "employee_id", "employee_name", "month", "year", 
                                 "pdf_data", "filename", "digital_signature", "sharing_channels"]
                
                if all(field in slip_data for field in required_fields):
                    # Verify digital signature structure
                    digital_signature = slip_data["digital_signature"]
                    signature_fields = ["signature_id", "verification_url", "qr_code_data", "timestamp"]
                    
                    if all(field in digital_signature for field in signature_fields):
                        # Verify PDF data is base64 encoded
                        try:
                            import base64
                            pdf_bytes = base64.b64decode(slip_data["pdf_data"])
                            pdf_valid = True
                            pdf_size = len(pdf_bytes)
                        except:
                            pdf_valid = False
                            pdf_size = 0
                            
                        if pdf_valid and pdf_size > 10000:  # Should be substantial with signature
                            self.log_result("digital_salary", "Generate Digital Salary Slip", True, 
                                          f"Successfully generated digital salary slip for {slip_data['employee_name']} "
                                          f"with signature ID: {digital_signature['signature_id']}, PDF size: {pdf_size} bytes")
                        else:
                            self.log_result("digital_salary", "Generate Digital Salary Slip", False, 
                                          f"Invalid or small PDF data: {pdf_size} bytes")
                    else:
                        missing_sig_fields = [field for field in signature_fields if field not in digital_signature]
                        self.log_result("digital_salary", "Generate Digital Salary Slip", False, 
                                      f"Missing digital signature fields: {missing_sig_fields}")
                else:
                    missing_fields = [field for field in required_fields if field not in slip_data]
                    self.log_result("digital_salary", "Generate Digital Salary Slip", False, 
                                  f"Missing fields in response: {missing_fields}")
            else:
                self.log_result("digital_salary", "Generate Digital Salary Slip", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("digital_salary", "Generate Digital Salary Slip", False, f"Exception: {str(e)}")
            
        # Test 2: Test with different month/year
        try:
            prev_month = current_month - 1 if current_month > 1 else 12
            prev_year = current_year if current_month > 1 else current_year - 1
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/generate-digital-salary-slip", 
                                   params={"month": prev_month, "year": prev_year}, headers=headers)
            
            if response.status_code == 200:
                slip_data = response.json()
                if slip_data.get("month") == prev_month and slip_data.get("year") == prev_year:
                    self.log_result("digital_salary", "Generate Different Month Slip", True, 
                                  f"Successfully generated slip for {prev_month}/{prev_year}")
                else:
                    self.log_result("digital_salary", "Generate Different Month Slip", False, 
                                  "Month/year mismatch in response")
            else:
                self.log_result("digital_salary", "Generate Different Month Slip", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("digital_salary", "Generate Different Month Slip", False, f"Exception: {str(e)}")
            
        # Test 3: Test with invalid employee ID
        try:
            invalid_employee_id = "INVALID123"
            response = requests.post(f"{self.base_url}/employees/{invalid_employee_id}/generate-digital-salary-slip", 
                                   params={"month": current_month, "year": current_year}, headers=headers)
            
            if response.status_code == 404:
                self.log_result("digital_salary", "Digital Slip Error Handling", True, 
                              "Correctly returned 404 for invalid employee ID")
            else:
                self.log_result("digital_salary", "Digital Slip Error Handling", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("digital_salary", "Digital Slip Error Handling", False, f"Exception: {str(e)}")
            
        # Test 4: Test authentication requirement
        try:
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/generate-digital-salary-slip", 
                                   params={"month": current_month, "year": current_year})  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("digital_salary", "Digital Salary Auth Required", True, 
                              "Correctly requires authentication for digital salary slip generation")
            else:
                self.log_result("digital_salary", "Digital Salary Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("digital_salary", "Digital Salary Auth Required", False, f"Exception: {str(e)}")
            
    def test_multi_channel_salary_sharing(self):
        """Test Multi-channel Salary Slip Sharing"""
        print("\n=== TESTING MULTI-CHANNEL SALARY SHARING ===")
        
        if not self.auth_token:
            self.log_result("multi_channel", "Multi-channel Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Use admin employee ID for testing
        test_employee_id = "VWT001"
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Test 1: Share salary slip via all channels
        try:
            sharing_params = {
                "month": current_month,
                "year": current_year,
                "channels": ["email", "whatsapp", "sms"]
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/share-salary-slip", 
                                   params=sharing_params, headers=headers)
            
            if response.status_code == 200:
                sharing_result = response.json()
                required_fields = ["message", "employee_id", "employee_name", "month", "year", 
                                 "channels_attempted", "sharing_results", "overall_status"]
                
                if all(field in sharing_result for field in required_fields):
                    sharing_results = sharing_result["sharing_results"]
                    channels_attempted = sharing_result["channels_attempted"]
                    
                    # Verify all channels were attempted
                    if all(channel in sharing_results for channel in channels_attempted):
                        # Count successful and failed deliveries
                        successful_channels = []
                        failed_channels = []
                        
                        for channel, result in sharing_results.items():
                            if result.get("status") == "success":
                                successful_channels.append(channel)
                            else:
                                failed_channels.append(channel)
                        
                        self.log_result("multi_channel", "Share All Channels", True, 
                                      f"Attempted sharing via {len(channels_attempted)} channels for {sharing_result['employee_name']} "
                                      f"- Successful: {successful_channels}, Failed: {failed_channels}")
                    else:
                        missing_channels = [ch for ch in channels_attempted if ch not in sharing_results]
                        self.log_result("multi_channel", "Share All Channels", False, 
                                      f"Missing sharing results for channels: {missing_channels}")
                else:
                    missing_fields = [field for field in required_fields if field not in sharing_result]
                    self.log_result("multi_channel", "Share All Channels", False, 
                                  f"Missing fields in response: {missing_fields}")
            else:
                self.log_result("multi_channel", "Share All Channels", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("multi_channel", "Share All Channels", False, f"Exception: {str(e)}")
            
        # Test 2: Share via single channel (email only)
        try:
            sharing_params = {
                "month": current_month,
                "year": current_year,
                "channels": ["email"]
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/share-salary-slip", 
                                   params=sharing_params, headers=headers)
            
            if response.status_code == 200:
                sharing_result = response.json()
                if len(sharing_result.get("channels_attempted", [])) == 1 and "email" in sharing_result["channels_attempted"]:
                    self.log_result("multi_channel", "Share Single Channel", True, 
                                  f"Successfully attempted email-only sharing")
                else:
                    self.log_result("multi_channel", "Share Single Channel", False, 
                                  f"Expected single email channel, got: {sharing_result.get('channels_attempted', [])}")
            else:
                self.log_result("multi_channel", "Share Single Channel", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("multi_channel", "Share Single Channel", False, f"Exception: {str(e)}")
            
        # Test 3: Share via WhatsApp and SMS only
        try:
            sharing_data = {
                "month": current_month,
                "year": current_year,
                "channels": ["whatsapp", "sms"]
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/share-salary-slip", 
                                   json=sharing_data, headers=headers)
            
            if response.status_code == 200:
                sharing_result = response.json()
                attempted_channels = sharing_result.get("channels_attempted", [])
                if len(attempted_channels) == 2 and "whatsapp" in attempted_channels and "sms" in attempted_channels:
                    self.log_result("multi_channel", "Share WhatsApp SMS", True, 
                                  f"Successfully attempted WhatsApp and SMS sharing")
                else:
                    self.log_result("multi_channel", "Share WhatsApp SMS", False, 
                                  f"Expected WhatsApp and SMS, got: {attempted_channels}")
            else:
                self.log_result("multi_channel", "Share WhatsApp SMS", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("multi_channel", "Share WhatsApp SMS", False, f"Exception: {str(e)}")
            
        # Test 4: Test with invalid employee ID
        try:
            invalid_employee_id = "INVALID123"
            sharing_data = {
                "month": current_month,
                "year": current_year,
                "channels": ["email"]
            }
            
            response = requests.post(f"{self.base_url}/employees/{invalid_employee_id}/share-salary-slip", 
                                   json=sharing_data, headers=headers)
            
            if response.status_code == 404:
                self.log_result("multi_channel", "Multi-channel Error Handling", True, 
                              "Correctly returned 404 for invalid employee ID")
            else:
                self.log_result("multi_channel", "Multi-channel Error Handling", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("multi_channel", "Multi-channel Error Handling", False, f"Exception: {str(e)}")
            
        # Test 5: Test authentication requirement
        try:
            sharing_data = {
                "month": current_month,
                "year": current_year,
                "channels": ["email"]
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/share-salary-slip", 
                                   json=sharing_data)  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("multi_channel", "Multi-channel Auth Required", True, 
                              "Correctly requires authentication for multi-channel sharing")
            else:
                self.log_result("multi_channel", "Multi-channel Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("multi_channel", "Multi-channel Auth Required", False, f"Exception: {str(e)}")
            
    def test_enhanced_dashboard(self):
        """Test Enhanced Dashboard Overview"""
        print("\n=== TESTING ENHANCED DASHBOARD ===")
        
        if not self.auth_token:
            self.log_result("enhanced_dashboard", "Enhanced Dashboard Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: Get comprehensive dashboard overview
        try:
            response = requests.get(f"{self.base_url}/dashboard/overview", headers=headers)
            
            if response.status_code == 200:
                dashboard_data = response.json()
                expected_sections = ["statistics", "last_updated"]
                
                if all(section in dashboard_data for section in expected_sections):
                    statistics = dashboard_data["statistics"]
                    expected_stats = ["employee_database", "interview_scheduled", "working_employees", 
                                    "announcements", "holidays"]
                    
                    if all(stat in statistics for stat in expected_stats):
                        # Verify statistics are numeric
                        stats_summary = []
                        for stat_name, stat_value in statistics.items():
                            if isinstance(stat_value, (int, float)) and stat_value >= 0:
                                stats_summary.append(f"{stat_name}: {stat_value}")
                            else:
                                stats_summary.append(f"{stat_name}: INVALID")
                        
                        self.log_result("enhanced_dashboard", "Get Dashboard Overview", True, 
                                      f"Successfully retrieved comprehensive dashboard - {', '.join(stats_summary)}")
                    else:
                        missing_stats = [stat for stat in expected_stats if stat not in statistics]
                        self.log_result("enhanced_dashboard", "Get Dashboard Overview", False, 
                                      f"Missing statistics: {missing_stats}")
                else:
                    missing_sections = [section for section in expected_sections if section not in dashboard_data]
                    self.log_result("enhanced_dashboard", "Get Dashboard Overview", False, 
                                  f"Missing dashboard sections: {missing_sections}")
            else:
                self.log_result("enhanced_dashboard", "Get Dashboard Overview", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("enhanced_dashboard", "Get Dashboard Overview", False, f"Exception: {str(e)}")
            
        # Test 2: Compare with basic dashboard stats
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats", headers=headers)
            
            if response.status_code == 200:
                basic_stats = response.json()
                basic_fields = ["total_employees", "present_today", "logged_in_now", "absent_today"]
                
                if all(field in basic_stats for field in basic_fields):
                    self.log_result("enhanced_dashboard", "Basic Dashboard Comparison", True, 
                                  f"Basic dashboard stats available for comparison - "
                                  f"Total: {basic_stats['total_employees']}, Present: {basic_stats['present_today']}")
                else:
                    self.log_result("enhanced_dashboard", "Basic Dashboard Comparison", False, 
                                  "Basic dashboard stats incomplete")
            else:
                self.log_result("enhanced_dashboard", "Basic Dashboard Comparison", False, 
                              f"Could not retrieve basic stats: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("enhanced_dashboard", "Basic Dashboard Comparison", False, f"Exception: {str(e)}")
            
        # Test 3: Test authentication requirement
        try:
            response = requests.get(f"{self.base_url}/dashboard/overview")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("enhanced_dashboard", "Dashboard Auth Required", True, 
                              "Correctly requires authentication for enhanced dashboard")
            else:
                self.log_result("enhanced_dashboard", "Dashboard Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("enhanced_dashboard", "Dashboard Auth Required", False, f"Exception: {str(e)}")
            
    def run_all_tests(self):
        """Run all enhanced HRMS tests"""
        print("🚀 STARTING ENHANCED HRMS BACKEND API TESTING")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
            
        # Run all test suites
        self.test_interview_scheduling_system()
        self.test_working_employee_database()
        self.test_holiday_calendar_management()
        self.test_digital_salary_slip_with_signature()
        self.test_multi_channel_salary_sharing()
        self.test_enhanced_dashboard()
        
        # Print summary
        self.print_test_summary()
        
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 ENHANCED HRMS TESTING SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status_icon = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
            print(f"{status_icon} {category.upper().replace('_', ' ')}: {passed} passed, {failed} failed")
            
            # Show failed tests
            if failed > 0:
                failed_tests = [detail for detail in results["details"] if detail["status"] == "❌ FAIL"]
                for test in failed_tests[:3]:  # Show first 3 failures
                    print(f"   ❌ {test['test']}: {test['message']}")
                if len(failed_tests) > 3:
                    print(f"   ... and {len(failed_tests) - 3} more failures")
        
        print("-" * 60)
        overall_status = "✅ SUCCESS" if total_failed == 0 else "⚠️ PARTIAL" if total_passed > total_failed else "❌ FAILED"
        print(f"{overall_status}: {total_passed} total passed, {total_failed} total failed")
        
        if total_failed == 0:
            print("🎉 All enhanced HRMS backend functionality is working perfectly!")
        else:
            print(f"⚠️ {total_failed} issues found that need attention.")

if __name__ == "__main__":
    tester = EnhancedHRMSTester()
    tester.run_all_tests()