#!/usr/bin/env python3
"""
Enhanced HRMS Bug Fix Testing Suite
Tests specific endpoints that were mentioned in the bug fix review request
"""

import requests
import json
from datetime import datetime, timezone
import time

# Configuration
BASE_URL = "https://vishwashrms.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
TEST_EMPLOYEE_ID = "VWT001"  # HR Administrator
TEST_MONTH = 1
TEST_YEAR = 2025

class EnhancedHRMSBugFixTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "working_employees": {"passed": 0, "failed": 0, "details": []},
            "holiday_calendar": {"passed": 0, "failed": 0, "details": []},
            "digital_salary_slip": {"passed": 0, "failed": 0, "details": []},
            "multi_channel_sharing": {"passed": 0, "failed": 0, "details": []},
            "interview_system": {"passed": 0, "failed": 0, "details": []},
            "dashboard_overview": {"passed": 0, "failed": 0, "details": []}
        }
        
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
        """Authenticate and get token"""
        print("\n=== AUTHENTICATION ===")
        
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
                    return True
                else:
                    self.log_result("authentication", "Admin Login", False, 
                                  "Response missing required fields", data)
                    return False
            else:
                self.log_result("authentication", "Admin Login", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("authentication", "Admin Login", False, f"Exception: {str(e)}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    def test_working_employee_database(self):
        """Test Working Employee Database - ObjectId serialization fix"""
        print("\n=== TESTING WORKING EMPLOYEE DATABASE (ObjectId Fix) ===")
        
        if not self.auth_token:
            self.log_result("working_employees", "Working Employee Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: GET /api/working-employees (ObjectId serialization fix)
        try:
            response = requests.get(f"{self.base_url}/working-employees", headers=headers)
            
            if response.status_code == 200:
                employees = response.json()
                if isinstance(employees, list):
                    if len(employees) > 0:
                        # Check if ObjectId serialization is working
                        first_employee = employees[0]
                        required_fields = ["id", "employee_id", "full_name", "department", "designation"]
                        
                        if all(field in first_employee for field in required_fields):
                            # Check if we can access all employee data without ObjectId errors
                            employee_count = len(employees)
                            self.log_result("working_employees", "GET Working Employees", True, 
                                          f"✅ FIXED: ObjectId serialization working - Retrieved {employee_count} employees successfully")
                        else:
                            missing_fields = [field for field in required_fields if field not in first_employee]
                            self.log_result("working_employees", "GET Working Employees", False, 
                                          f"Missing required fields: {missing_fields}")
                    else:
                        self.log_result("working_employees", "GET Working Employees", True, 
                                      "✅ Endpoint working but no employees found")
                else:
                    self.log_result("working_employees", "GET Working Employees", False, 
                                  "Response is not a list")
            else:
                self.log_result("working_employees", "GET Working Employees", False, 
                              f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("working_employees", "GET Working Employees", False, f"Exception: {str(e)}")
            
        # Test 2: GET /api/working-employees with department filter
        try:
            response = requests.get(f"{self.base_url}/working-employees?department=Administration", headers=headers)
            
            if response.status_code == 200:
                employees = response.json()
                if isinstance(employees, list):
                    self.log_result("working_employees", "GET Working Employees with Filter", True, 
                                  f"Department filter working - Retrieved {len(employees)} employees")
                else:
                    self.log_result("working_employees", "GET Working Employees with Filter", False, 
                                  "Response is not a list")
            else:
                self.log_result("working_employees", "GET Working Employees with Filter", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("working_employees", "GET Working Employees with Filter", False, f"Exception: {str(e)}")
            
    def test_holiday_calendar(self):
        """Test Holiday Calendar - Date serialization fixes"""
        print("\n=== TESTING HOLIDAY CALENDAR (Date Serialization Fix) ===")
        
        if not self.auth_token:
            self.log_result("holiday_calendar", "Holiday Calendar Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: POST /api/holidays (date serialization fix)
        try:
            holiday_data = {
                "holiday_name": "Test Company Holiday",
                "holiday_date": "2025-03-15",
                "holiday_type": "Company",
                "description": "Test holiday for bug fix verification",
                "is_mandatory": True,
                "applicable_locations": ["Bangalore"]
            }
            
            response = requests.post(f"{self.base_url}/holidays", json=holiday_data, headers=headers)
            
            if response.status_code == 200:
                created_holiday = response.json()
                if "id" in created_holiday and "holiday_name" in created_holiday:
                    self.log_result("holiday_calendar", "POST Create Holiday", True, 
                                  f"✅ FIXED: Date serialization working - Created holiday '{created_holiday['holiday_name']}'")
                else:
                    self.log_result("holiday_calendar", "POST Create Holiday", False, 
                                  "Response missing required fields")
            else:
                self.log_result("holiday_calendar", "POST Create Holiday", False, 
                              f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("holiday_calendar", "POST Create Holiday", False, f"Exception: {str(e)}")
            
        # Test 2: GET /api/holidays/{year} (MongoDB date query issue)
        try:
            response = requests.get(f"{self.base_url}/holidays/{TEST_YEAR}", headers=headers)
            
            if response.status_code == 200:
                holiday_data = response.json()
                if "year" in holiday_data and "holidays" in holiday_data:
                    holidays = holiday_data["holidays"]
                    if isinstance(holidays, list):
                        self.log_result("holiday_calendar", "GET Yearly Holidays", True, 
                                      f"✅ FIXED: MongoDB date query working - Retrieved {len(holidays)} holidays for {TEST_YEAR}")
                    else:
                        self.log_result("holiday_calendar", "GET Yearly Holidays", False, 
                                      "Holidays field is not a list")
                else:
                    self.log_result("holiday_calendar", "GET Yearly Holidays", False, 
                                  "Response missing required fields")
            else:
                self.log_result("holiday_calendar", "GET Yearly Holidays", False, 
                              f"❌ STILL FAILING: HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("holiday_calendar", "GET Yearly Holidays", False, f"Exception: {str(e)}")
            
        # Test 3: GET /api/holidays/2024 (test different year)
        try:
            response = requests.get(f"{self.base_url}/holidays/2024", headers=headers)
            
            if response.status_code == 200:
                holiday_data = response.json()
                if "year" in holiday_data and "holidays" in holiday_data:
                    self.log_result("holiday_calendar", "GET Different Year Holidays", True, 
                                  f"Different year query working - Retrieved {len(holiday_data['holidays'])} holidays for 2024")
                else:
                    self.log_result("holiday_calendar", "GET Different Year Holidays", False, 
                                  "Response missing required fields")
            else:
                self.log_result("holiday_calendar", "GET Different Year Holidays", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("holiday_calendar", "GET Different Year Holidays", False, f"Exception: {str(e)}")
            
    def test_digital_salary_slip(self):
        """Test Digital Salary Slip - Function signature fix"""
        print("\n=== TESTING DIGITAL SALARY SLIP (Function Signature Fix) ===")
        
        if not self.auth_token:
            self.log_result("digital_salary_slip", "Digital Salary Slip Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: POST /api/employees/{employee_id}/generate-digital-salary-slip (function signature fix)
        try:
            response = requests.post(
                f"{self.base_url}/employees/{TEST_EMPLOYEE_ID}/generate-digital-salary-slip",
                params={"month": TEST_MONTH, "year": TEST_YEAR},
                headers=headers
            )
            
            if response.status_code == 200:
                slip_data = response.json()
                required_fields = ["message", "employee_id", "employee_name", "month", "year", "pdf_data", "filename"]
                
                if all(field in slip_data for field in required_fields):
                    # Verify PDF data is base64 encoded
                    try:
                        import base64
                        pdf_bytes = base64.b64decode(slip_data["pdf_data"])
                        pdf_valid = True
                        pdf_size = len(pdf_bytes)
                    except:
                        pdf_valid = False
                        pdf_size = 0
                        
                    if pdf_valid and slip_data["employee_id"] == TEST_EMPLOYEE_ID:
                        self.log_result("digital_salary_slip", "Generate Digital Salary Slip", True, 
                                      f"✅ FIXED: Function signature working - Generated digital salary slip for {slip_data['employee_name']}, PDF size: {pdf_size} bytes")
                    else:
                        self.log_result("digital_salary_slip", "Generate Digital Salary Slip", False, 
                                      "Invalid PDF data or employee ID mismatch")
                else:
                    missing_fields = [field for field in required_fields if field not in slip_data]
                    self.log_result("digital_salary_slip", "Generate Digital Salary Slip", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("digital_salary_slip", "Generate Digital Salary Slip", False, 
                              f"❌ STILL FAILING: HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("digital_salary_slip", "Generate Digital Salary Slip", False, f"Exception: {str(e)}")
            
        # Test 2: Test with invalid employee ID
        try:
            response = requests.post(
                f"{self.base_url}/employees/INVALID123/generate-digital-salary-slip",
                params={"month": TEST_MONTH, "year": TEST_YEAR},
                headers=headers
            )
            
            if response.status_code == 404:
                self.log_result("digital_salary_slip", "Digital Salary Slip Error Handling", True, 
                              "Correctly returned 404 for invalid employee ID")
            else:
                self.log_result("digital_salary_slip", "Digital Salary Slip Error Handling", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("digital_salary_slip", "Digital Salary Slip Error Handling", False, f"Exception: {str(e)}")
            
    def test_multi_channel_sharing(self):
        """Test Multi-channel Salary Slip Sharing - JSON body format and function fix"""
        print("\n=== TESTING MULTI-CHANNEL SHARING (JSON Body Format & Function Fix) ===")
        
        if not self.auth_token:
            self.log_result("multi_channel_sharing", "Multi-channel Sharing Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: POST /api/employees/{employee_id}/share-salary-slip (JSON body format and function fix)
        try:
            share_request = {
                "month": TEST_MONTH,
                "year": TEST_YEAR,
                "channels": ["email", "whatsapp"]
            }
            
            response = requests.post(
                f"{self.base_url}/employees/{TEST_EMPLOYEE_ID}/share-salary-slip",
                json=share_request,
                headers=headers
            )
            
            if response.status_code == 200:
                share_data = response.json()
                required_fields = ["message", "employee_id", "employee_name", "month", "year", "channels_attempted", "sharing_results"]
                
                if all(field in share_data for field in required_fields):
                    sharing_results = share_data.get("sharing_results", {})
                    channels_attempted = share_data.get("channels_attempted", [])
                    
                    if share_data["employee_id"] == TEST_EMPLOYEE_ID and len(channels_attempted) > 0:
                        self.log_result("multi_channel_sharing", "Share Salary Slip Multi-channel", True, 
                                      f"✅ FIXED: JSON body format and function working - Attempted sharing via {channels_attempted} for {share_data['employee_name']}")
                    else:
                        self.log_result("multi_channel_sharing", "Share Salary Slip Multi-channel", False, 
                                      "Employee ID mismatch or no channels attempted")
                else:
                    missing_fields = [field for field in required_fields if field not in share_data]
                    self.log_result("multi_channel_sharing", "Share Salary Slip Multi-channel", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("multi_channel_sharing", "Share Salary Slip Multi-channel", False, 
                              f"❌ STILL FAILING: HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("multi_channel_sharing", "Share Salary Slip Multi-channel", False, f"Exception: {str(e)}")
            
        # Test 2: Test with single channel
        try:
            share_request = {
                "month": TEST_MONTH,
                "year": TEST_YEAR,
                "channels": ["email"]
            }
            
            response = requests.post(
                f"{self.base_url}/employees/{TEST_EMPLOYEE_ID}/share-salary-slip",
                json=share_request,
                headers=headers
            )
            
            if response.status_code == 200:
                share_data = response.json()
                if "sharing_results" in share_data:
                    self.log_result("multi_channel_sharing", "Share Single Channel", True, 
                                  f"Single channel sharing working - Email channel attempted")
                else:
                    self.log_result("multi_channel_sharing", "Share Single Channel", False, 
                                  "Response missing sharing_results")
            else:
                self.log_result("multi_channel_sharing", "Share Single Channel", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("multi_channel_sharing", "Share Single Channel", False, f"Exception: {str(e)}")
            
        # Test 3: Test with all channels
        try:
            share_request = {
                "month": TEST_MONTH,
                "year": TEST_YEAR,
                "channels": ["email", "whatsapp", "sms"]
            }
            
            response = requests.post(
                f"{self.base_url}/employees/{TEST_EMPLOYEE_ID}/share-salary-slip",
                json=share_request,
                headers=headers
            )
            
            if response.status_code == 200:
                share_data = response.json()
                channels_attempted = share_data.get("channels_attempted", [])
                if len(channels_attempted) == 3:
                    self.log_result("multi_channel_sharing", "Share All Channels", True, 
                                  f"All channels sharing working - {channels_attempted} attempted")
                else:
                    self.log_result("multi_channel_sharing", "Share All Channels", False, 
                                  f"Expected 3 channels, got {len(channels_attempted)}")
            else:
                self.log_result("multi_channel_sharing", "Share All Channels", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("multi_channel_sharing", "Share All Channels", False, f"Exception: {str(e)}")
            
    def test_interview_system(self):
        """Test Interview System - Should still be working"""
        print("\n=== TESTING INTERVIEW SYSTEM (Should Still Work) ===")
        
        if not self.auth_token:
            self.log_result("interview_system", "Interview System Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: POST /api/interviews
        try:
            interview_data = {
                "candidate_name": "Priya Sharma",
                "candidate_email": "priya.sharma@email.com",
                "candidate_phone": "+91-9876543210",
                "position": "Software Developer",
                "department": "Technology",
                "interview_type": "Technical",
                "interview_date": "2025-02-15T10:00:00Z",
                "interviewer": "Tech Lead",
                "interview_mode": "In-person",
                "interview_location": "Bangalore Office",
                "interview_status": "Scheduled"
            }
            
            response = requests.post(f"{self.base_url}/interviews", json=interview_data, headers=headers)
            
            if response.status_code == 200:
                created_interview = response.json()
                if "id" in created_interview and "candidate_name" in created_interview:
                    self.log_result("interview_system", "POST Create Interview", True, 
                                  f"✅ Interview creation working - Created interview for {created_interview['candidate_name']}")
                else:
                    self.log_result("interview_system", "POST Create Interview", False, 
                                  "Response missing required fields")
            else:
                self.log_result("interview_system", "POST Create Interview", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("interview_system", "POST Create Interview", False, f"Exception: {str(e)}")
            
        # Test 2: GET /api/interviews
        try:
            response = requests.get(f"{self.base_url}/interviews", headers=headers)
            
            if response.status_code == 200:
                interviews = response.json()
                if isinstance(interviews, list):
                    self.log_result("interview_system", "GET All Interviews", True, 
                                  f"✅ Interview retrieval working - Retrieved {len(interviews)} interviews")
                else:
                    self.log_result("interview_system", "GET All Interviews", False, 
                                  "Response is not a list")
            else:
                self.log_result("interview_system", "GET All Interviews", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("interview_system", "GET All Interviews", False, f"Exception: {str(e)}")
            
        # Test 3: GET /api/interviews with status filter
        try:
            response = requests.get(f"{self.base_url}/interviews?status=Scheduled", headers=headers)
            
            if response.status_code == 200:
                interviews = response.json()
                if isinstance(interviews, list):
                    self.log_result("interview_system", "GET Interviews with Filter", True, 
                                  f"Interview filtering working - Retrieved {len(interviews)} scheduled interviews")
                else:
                    self.log_result("interview_system", "GET Interviews with Filter", False, 
                                  "Response is not a list")
            else:
                self.log_result("interview_system", "GET Interviews with Filter", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("interview_system", "GET Interviews with Filter", False, f"Exception: {str(e)}")
            
    def test_dashboard_overview(self):
        """Test Dashboard Overview - Should still be working"""
        print("\n=== TESTING DASHBOARD OVERVIEW (Should Still Work) ===")
        
        if not self.auth_token:
            self.log_result("dashboard_overview", "Dashboard Overview Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: GET /api/dashboard/overview
        try:
            response = requests.get(f"{self.base_url}/dashboard/overview", headers=headers)
            
            if response.status_code == 200:
                overview_data = response.json()
                if "statistics" in overview_data and "last_updated" in overview_data:
                    statistics = overview_data["statistics"]
                    expected_stats = ["employee_database", "interview_scheduled", "working_employees", "announcements", "holidays"]
                    
                    if all(stat in statistics for stat in expected_stats):
                        self.log_result("dashboard_overview", "GET Dashboard Overview", True, 
                                      f"✅ Dashboard overview working - Retrieved comprehensive statistics: {statistics}")
                    else:
                        missing_stats = [stat for stat in expected_stats if stat not in statistics]
                        self.log_result("dashboard_overview", "GET Dashboard Overview", False, 
                                      f"Missing statistics: {missing_stats}")
                else:
                    self.log_result("dashboard_overview", "GET Dashboard Overview", False, 
                                  "Response missing required fields")
            else:
                self.log_result("dashboard_overview", "GET Dashboard Overview", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("dashboard_overview", "GET Dashboard Overview", False, f"Exception: {str(e)}")
            
    def run_all_tests(self):
        """Run all bug fix tests"""
        print("🔧 ENHANCED HRMS BUG FIX TESTING SUITE")
        print("=" * 60)
        print(f"Testing specific bug fixes with:")
        print(f"- Employee: {TEST_EMPLOYEE_ID}")
        print(f"- Month/Year: {TEST_MONTH}/{TEST_YEAR}")
        print(f"- Base URL: {self.base_url}")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return
            
        # Run all tests
        self.test_working_employee_database()
        self.test_holiday_calendar()
        self.test_digital_salary_slip()
        self.test_multi_channel_sharing()
        self.test_interview_system()
        self.test_dashboard_overview()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🔧 BUG FIX TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            if passed + failed > 0:
                print(f"\n{category.upper().replace('_', ' ')}:")
                print(f"  ✅ Passed: {passed}")
                print(f"  ❌ Failed: {failed}")
                
                # Show failed tests
                for detail in results["details"]:
                    if detail["status"] == "❌ FAIL":
                        print(f"    - {detail['test']}: {detail['message']}")
        
        print(f"\n{'='*60}")
        print(f"OVERALL RESULTS:")
        print(f"✅ Total Passed: {total_passed}")
        print(f"❌ Total Failed: {total_failed}")
        
        if total_failed == 0:
            print("🎉 ALL BUG FIXES VERIFIED SUCCESSFULLY!")
        else:
            print(f"⚠️  {total_failed} ISSUES STILL NEED ATTENTION")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = EnhancedHRMSBugFixTester()
    tester.run_all_tests()