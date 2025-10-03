#!/usr/bin/env python3
"""
HRMS Backend Bug Fix Testing Suite
Tests specific bug fixes for the enhanced HRMS backend endpoints
"""

import requests
import json
from datetime import datetime, timezone, date
import uuid
import time

# Configuration
BASE_URL = "https://vishwashrms.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class HRMSBugFixTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_results = {
            "working_employees": {"passed": 0, "failed": 0, "details": []},
            "holiday_calendar": {"passed": 0, "failed": 0, "details": []},
            "digital_salary_slip": {"passed": 0, "failed": 0, "details": []},
            "multi_channel_sharing": {"passed": 0, "failed": 0, "details": []}
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
        """Authenticate and get JWT token"""
        print("\n=== AUTHENTICATING ===")
        
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
                    print(f"✅ Successfully authenticated as {data['employee']['full_name']}")
                    return True
                else:
                    print("❌ Authentication failed - missing access token")
                    return False
            else:
                print(f"❌ Authentication failed - HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication exception: {str(e)}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    def test_working_employees_fix(self):
        """Test Working Employee Database Fix - ObjectId serialization"""
        print("\n=== TESTING WORKING EMPLOYEE DATABASE FIX ===")
        
        if not self.auth_token:
            self.log_result("working_employees", "Working Employees Test", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: GET /api/working-employees (should handle ObjectId serialization properly)
        try:
            response = requests.get(f"{self.base_url}/working-employees", headers=headers)
            
            if response.status_code == 200:
                employees = response.json()
                if isinstance(employees, list):
                    # Check if we have at least one employee
                    if len(employees) > 0:
                        # Verify the structure of the first employee
                        first_employee = employees[0]
                        required_fields = ["employee_id", "full_name", "department", "designation"]
                        
                        if all(field in first_employee for field in required_fields):
                            self.log_result("working_employees", "GET Working Employees", True, 
                                          f"✅ Successfully retrieved {len(employees)} working employees with proper ObjectId serialization")
                        else:
                            missing_fields = [field for field in required_fields if field not in first_employee]
                            self.log_result("working_employees", "GET Working Employees", False, 
                                          f"Missing required fields: {missing_fields}")
                    else:
                        self.log_result("working_employees", "GET Working Employees", True, 
                                      "✅ Successfully retrieved working employees list (empty but no serialization error)")
                else:
                    self.log_result("working_employees", "GET Working Employees", False, 
                                  "Response is not a list")
            elif response.status_code == 500:
                self.log_result("working_employees", "GET Working Employees", False, 
                              f"❌ CRITICAL: Still getting HTTP 500 - ObjectId serialization not fixed. Response: {response.text}")
            else:
                self.log_result("working_employees", "GET Working Employees", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("working_employees", "GET Working Employees", False, f"Exception: {str(e)}")
            
        # Test 2: Test with department filter
        try:
            response = requests.get(f"{self.base_url}/working-employees?department=HR", headers=headers)
            
            if response.status_code == 200:
                employees = response.json()
                if isinstance(employees, list):
                    self.log_result("working_employees", "Working Employees with Filter", True, 
                                  f"✅ Department filter working - retrieved {len(employees)} HR employees")
                else:
                    self.log_result("working_employees", "Working Employees with Filter", False, 
                                  "Response is not a list")
            else:
                self.log_result("working_employees", "Working Employees with Filter", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("working_employees", "Working Employees with Filter", False, f"Exception: {str(e)}")
            
    def test_holiday_calendar_fix(self):
        """Test Holiday Calendar Fix - Date serialization"""
        print("\n=== TESTING HOLIDAY CALENDAR FIX ===")
        
        if not self.auth_token:
            self.log_result("holiday_calendar", "Holiday Calendar Test", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: POST /api/holidays (should handle date serialization properly)
        try:
            holiday_data = {
                "holiday_name": "Test Holiday Fix",
                "holiday_date": "2025-03-15",  # String format date
                "holiday_type": "Company",
                "description": "Testing date serialization fix",
                "is_mandatory": True,
                "applicable_locations": ["Bangalore", "Mumbai"]
            }
            
            response = requests.post(f"{self.base_url}/holidays", json=holiday_data, headers=headers)
            
            if response.status_code == 200:
                created_holiday = response.json()
                required_fields = ["id", "holiday_name", "holiday_date", "holiday_type"]
                
                if all(field in created_holiday for field in required_fields):
                    if created_holiday["holiday_name"] == "Test Holiday Fix":
                        self.log_result("holiday_calendar", "POST Create Holiday", True, 
                                      f"✅ Successfully created holiday with proper date serialization: {created_holiday['holiday_name']} on {created_holiday['holiday_date']}")
                    else:
                        self.log_result("holiday_calendar", "POST Create Holiday", False, 
                                      "Holiday data mismatch")
                else:
                    missing_fields = [field for field in required_fields if field not in created_holiday]
                    self.log_result("holiday_calendar", "POST Create Holiday", False, 
                                  f"Missing fields: {missing_fields}")
            elif response.status_code == 500 and "cannot encode object: datetime.date" in response.text:
                self.log_result("holiday_calendar", "POST Create Holiday", False, 
                              f"❌ CRITICAL: Date serialization error still exists. Response: {response.text}")
            else:
                self.log_result("holiday_calendar", "POST Create Holiday", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("holiday_calendar", "POST Create Holiday", False, f"Exception: {str(e)}")
            
        # Test 2: GET /api/holidays/{year} (should work correctly)
        try:
            current_year = datetime.now().year
            response = requests.get(f"{self.base_url}/holidays/{current_year}", headers=headers)
            
            if response.status_code == 200:
                holiday_data = response.json()
                required_fields = ["year", "holidays", "total_holidays"]
                
                if all(field in holiday_data for field in required_fields):
                    holidays = holiday_data["holidays"]
                    if isinstance(holidays, list):
                        self.log_result("holiday_calendar", "GET Holiday Calendar", True, 
                                      f"✅ Successfully retrieved {len(holidays)} holidays for {current_year}")
                    else:
                        self.log_result("holiday_calendar", "GET Holiday Calendar", False, 
                                      "Holidays field is not a list")
                else:
                    missing_fields = [field for field in required_fields if field not in holiday_data]
                    self.log_result("holiday_calendar", "GET Holiday Calendar", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("holiday_calendar", "GET Holiday Calendar", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("holiday_calendar", "GET Holiday Calendar", False, f"Exception: {str(e)}")
            
        # Test 3: Test with different date formats
        try:
            holiday_data_2 = {
                "holiday_name": "Test Holiday Fix 2",
                "holiday_date": "2025-06-20",
                "holiday_type": "National",
                "description": "Testing different date format",
                "is_mandatory": False,
                "applicable_locations": ["All"]
            }
            
            response = requests.post(f"{self.base_url}/holidays", json=holiday_data_2, headers=headers)
            
            if response.status_code == 200:
                self.log_result("holiday_calendar", "POST Holiday Different Date Format", True, 
                              "✅ Successfully created holiday with different date format")
            else:
                self.log_result("holiday_calendar", "POST Holiday Different Date Format", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("holiday_calendar", "POST Holiday Different Date Format", False, f"Exception: {str(e)}")
            
    def test_digital_salary_slip_fix(self):
        """Test Digital Salary Slip Fix - Function signature"""
        print("\n=== TESTING DIGITAL SALARY SLIP FIX ===")
        
        if not self.auth_token:
            self.log_result("digital_salary_slip", "Digital Salary Slip Test", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Use existing employee EMP001 for testing
        test_employee_id = "EMP001"
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Test 1: POST /api/employees/{employee_id}/generate-digital-salary-slip (function signature should be fixed)
        try:
            response = requests.post(
                f"{self.base_url}/employees/{test_employee_id}/generate-digital-salary-slip",
                params={"month": current_month, "year": current_year},
                headers=headers
            )
            
            if response.status_code == 200:
                slip_data = response.json()
                required_fields = ["message", "employee_id", "employee_name", "month", "year", "pdf_data", "filename", "digital_signature"]
                
                if all(field in slip_data for field in required_fields):
                    # Verify PDF data is base64 encoded
                    try:
                        import base64
                        base64.b64decode(slip_data["pdf_data"])
                        pdf_valid = True
                    except:
                        pdf_valid = False
                        
                    if pdf_valid and slip_data["employee_id"] == test_employee_id:
                        # Check digital signature info
                        digital_signature = slip_data.get("digital_signature", {})
                        if isinstance(digital_signature, dict) and "verification_url" in digital_signature:
                            self.log_result("digital_salary_slip", "Generate Digital Salary Slip", True, 
                                          f"✅ Successfully generated digital salary slip for {slip_data['employee_name']} with QR signature")
                        else:
                            self.log_result("digital_salary_slip", "Generate Digital Salary Slip", False, 
                                          "Digital signature info missing or invalid")
                    else:
                        self.log_result("digital_salary_slip", "Generate Digital Salary Slip", False, 
                                      f"Invalid PDF data or employee ID mismatch")
                else:
                    missing_fields = [field for field in required_fields if field not in slip_data]
                    self.log_result("digital_salary_slip", "Generate Digital Salary Slip", False, 
                                  f"Missing fields: {missing_fields}")
            elif response.status_code == 500 and "takes 0 positional arguments but 3 were given" in response.text:
                self.log_result("digital_salary_slip", "Generate Digital Salary Slip", False, 
                              f"❌ CRITICAL: Function signature error still exists. Response: {response.text}")
            else:
                self.log_result("digital_salary_slip", "Generate Digital Salary Slip", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("digital_salary_slip", "Generate Digital Salary Slip", False, f"Exception: {str(e)}")
            
        # Test 2: Test with invalid employee ID
        try:
            response = requests.post(
                f"{self.base_url}/employees/INVALID123/generate-digital-salary-slip",
                params={"month": current_month, "year": current_year},
                headers=headers
            )
            
            if response.status_code == 404:
                self.log_result("digital_salary_slip", "Digital Salary Slip Invalid Employee", True, 
                              "✅ Correctly returned 404 for invalid employee ID")
            else:
                self.log_result("digital_salary_slip", "Digital Salary Slip Invalid Employee", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("digital_salary_slip", "Digital Salary Slip Invalid Employee", False, f"Exception: {str(e)}")
            
        # Test 3: Test authentication requirement
        try:
            response = requests.post(
                f"{self.base_url}/employees/{test_employee_id}/generate-digital-salary-slip",
                params={"month": current_month, "year": current_year}
            )  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("digital_salary_slip", "Digital Salary Slip Auth Required", True, 
                              "✅ Correctly requires authentication")
            else:
                self.log_result("digital_salary_slip", "Digital Salary Slip Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("digital_salary_slip", "Digital Salary Slip Auth Required", False, f"Exception: {str(e)}")
            
    def test_multi_channel_sharing_fix(self):
        """Test Multi-channel Sharing Fix - JSON body format"""
        print("\n=== TESTING MULTI-CHANNEL SHARING FIX ===")
        
        if not self.auth_token:
            self.log_result("multi_channel_sharing", "Multi-channel Sharing Test", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Use existing employee EMP001 for testing
        test_employee_id = "EMP001"
        
        # Test 1: POST /api/employees/{employee_id}/share-salary-slip (should accept JSON body)
        try:
            request_data = {
                "month": 1,
                "year": 2025,
                "channels": ["email", "whatsapp", "sms"]
            }
            
            response = requests.post(
                f"{self.base_url}/employees/{test_employee_id}/share-salary-slip",
                json=request_data,  # JSON body format as specified
                headers=headers
            )
            
            if response.status_code == 200:
                sharing_data = response.json()
                required_fields = ["message", "employee_id", "employee_name", "month", "year", "channels_attempted", "sharing_results"]
                
                if all(field in sharing_data for field in required_fields):
                    sharing_results = sharing_data.get("sharing_results", {})
                    channels_attempted = sharing_data.get("channels_attempted", [])
                    
                    if sharing_data["employee_id"] == test_employee_id and len(channels_attempted) == 3:
                        # Check if sharing results contain all channels
                        expected_channels = ["email", "whatsapp", "sms"]
                        if all(channel in sharing_results for channel in expected_channels):
                            self.log_result("multi_channel_sharing", "Multi-channel Salary Slip Sharing", True, 
                                          f"✅ Successfully processed multi-channel sharing for {sharing_data['employee_name']} via {', '.join(channels_attempted)}")
                        else:
                            missing_channels = [ch for ch in expected_channels if ch not in sharing_results]
                            self.log_result("multi_channel_sharing", "Multi-channel Salary Slip Sharing", False, 
                                          f"Missing sharing results for channels: {missing_channels}")
                    else:
                        self.log_result("multi_channel_sharing", "Multi-channel Salary Slip Sharing", False, 
                                      f"Employee ID mismatch or incorrect channels count")
                else:
                    missing_fields = [field for field in required_fields if field not in sharing_data]
                    self.log_result("multi_channel_sharing", "Multi-channel Salary Slip Sharing", False, 
                                  f"Missing fields: {missing_fields}")
            elif response.status_code == 422 and "Field required" in response.text:
                self.log_result("multi_channel_sharing", "Multi-channel Salary Slip Sharing", False, 
                              f"❌ CRITICAL: API parameter parsing still failing. Response: {response.text}")
            else:
                self.log_result("multi_channel_sharing", "Multi-channel Salary Slip Sharing", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("multi_channel_sharing", "Multi-channel Salary Slip Sharing", False, f"Exception: {str(e)}")
            
        # Test 2: Test with single channel
        try:
            request_data = {
                "month": 2,
                "year": 2025,
                "channels": ["email"]
            }
            
            response = requests.post(
                f"{self.base_url}/employees/{test_employee_id}/share-salary-slip",
                json=request_data,
                headers=headers
            )
            
            if response.status_code == 200:
                sharing_data = response.json()
                channels_attempted = sharing_data.get("channels_attempted", [])
                if len(channels_attempted) == 1 and channels_attempted[0] == "email":
                    self.log_result("multi_channel_sharing", "Single Channel Sharing", True, 
                                  "✅ Successfully processed single channel (email) sharing")
                else:
                    self.log_result("multi_channel_sharing", "Single Channel Sharing", False, 
                                  f"Expected single email channel, got: {channels_attempted}")
            else:
                self.log_result("multi_channel_sharing", "Single Channel Sharing", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("multi_channel_sharing", "Single Channel Sharing", False, f"Exception: {str(e)}")
            
        # Test 3: Test with invalid employee ID
        try:
            request_data = {
                "month": 1,
                "year": 2025,
                "channels": ["email"]
            }
            
            response = requests.post(
                f"{self.base_url}/employees/INVALID123/share-salary-slip",
                json=request_data,
                headers=headers
            )
            
            if response.status_code == 404:
                self.log_result("multi_channel_sharing", "Multi-channel Sharing Invalid Employee", True, 
                              "✅ Correctly returned 404 for invalid employee ID")
            else:
                self.log_result("multi_channel_sharing", "Multi-channel Sharing Invalid Employee", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("multi_channel_sharing", "Multi-channel Sharing Invalid Employee", False, f"Exception: {str(e)}")
            
        # Test 4: Test authentication requirement
        try:
            request_data = {
                "month": 1,
                "year": 2025,
                "channels": ["email"]
            }
            
            response = requests.post(
                f"{self.base_url}/employees/{test_employee_id}/share-salary-slip",
                json=request_data
            )  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("multi_channel_sharing", "Multi-channel Sharing Auth Required", True, 
                              "✅ Correctly requires authentication")
            else:
                self.log_result("multi_channel_sharing", "Multi-channel Sharing Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("multi_channel_sharing", "Multi-channel Sharing Auth Required", False, f"Exception: {str(e)}")
            
    def run_all_tests(self):
        """Run all bug fix tests"""
        print("🔧 HRMS Backend Bug Fix Testing Suite")
        print("=" * 50)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
            
        # Run all bug fix tests
        self.test_working_employees_fix()
        self.test_holiday_calendar_fix()
        self.test_digital_salary_slip_fix()
        self.test_multi_channel_sharing_fix()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("🔧 BUG FIX TEST SUMMARY")
        print("=" * 50)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            category_name = category.replace("_", " ").title()
            print(f"\n{category_name}:")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            
            # Show failed test details
            if failed > 0:
                print("  Failed Tests:")
                for detail in results["details"]:
                    if detail["status"] == "❌ FAIL":
                        print(f"    - {detail['test']}: {detail['message']}")
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Total Passed: {total_passed}")
        print(f"❌ Total Failed: {total_failed}")
        print(f"📈 Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%" if (total_passed + total_failed) > 0 else "0.0%")
        
        if total_failed == 0:
            print("\n🎉 ALL BUG FIXES VERIFIED SUCCESSFULLY!")
        else:
            print(f"\n⚠️  {total_failed} CRITICAL ISSUES STILL NEED ATTENTION")

if __name__ == "__main__":
    tester = HRMSBugFixTester()
    tester.run_all_tests()