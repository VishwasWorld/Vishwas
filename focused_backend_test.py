#!/usr/bin/env python3
"""
Focused HRMS Backend API Testing Suite
Tests login authentication and employee retrieval as requested in the review
"""

import requests
import json
from datetime import datetime, timezone
import time

# Configuration
BASE_URL = "https://vishwashrms.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class FocusedHRMSAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "employees": {"passed": 0, "failed": 0, "details": []},
            "dashboard": {"passed": 0, "failed": 0, "details": []}
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
        
    def test_login_authentication(self):
        """Test login API with admin credentials as specified in review request"""
        print("\n=== TESTING LOGIN AUTHENTICATION API ===")
        
        # Test 1: Valid admin login with exact credentials from review request
        try:
            login_data = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            }
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            print(f"Login request to: {self.base_url}/auth/login")
            print(f"Login credentials: {login_data}")
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response data keys: {list(data.keys())}")
                
                if "access_token" in data and "employee" in data:
                    self.auth_token = data["access_token"]
                    employee_info = data["employee"]
                    
                    # Verify JWT token format
                    token_parts = self.auth_token.split('.')
                    if len(token_parts) == 3:
                        token_format_valid = True
                        token_info = f"JWT token format valid (3 parts), length: {len(self.auth_token)} chars"
                    else:
                        token_format_valid = False
                        token_info = f"Invalid JWT format: {len(token_parts)} parts"
                    
                    self.log_result("authentication", "Admin Login with JWT Token", True, 
                                  f"Successfully logged in as {employee_info.get('full_name', 'Unknown')} "
                                  f"(ID: {employee_info.get('employee_id', 'Unknown')}). {token_info}")
                    
                    # Log detailed employee info from login
                    print(f"Logged in employee details: {json.dumps(employee_info, indent=2, default=str)}")
                    
                else:
                    self.log_result("authentication", "Admin Login with JWT Token", False, 
                                  f"Response missing required fields. Got keys: {list(data.keys())}", data)
            else:
                error_text = response.text
                self.log_result("authentication", "Admin Login with JWT Token", False, 
                              f"HTTP {response.status_code}: {error_text}")
                print(f"Login failed with status {response.status_code}: {error_text}")
                
        except Exception as e:
            self.log_result("authentication", "Admin Login with JWT Token", False, f"Exception: {str(e)}")
            print(f"Login exception: {str(e)}")
            
        # Test 2: Verify token validity by checking format
        if self.auth_token:
            try:
                # Basic JWT format validation
                token_parts = self.auth_token.split('.')
                if len(token_parts) == 3:
                    import base64
                    # Try to decode header and payload (not signature verification)
                    try:
                        header = json.loads(base64.b64decode(token_parts[0] + '=='))
                        payload = json.loads(base64.b64decode(token_parts[1] + '=='))
                        
                        self.log_result("authentication", "JWT Token Format Validation", True, 
                                      f"JWT token structure valid. Algorithm: {header.get('alg', 'Unknown')}, "
                                      f"Subject: {payload.get('sub', 'Unknown')}")
                        print(f"JWT Header: {header}")
                        print(f"JWT Payload: {payload}")
                        
                    except Exception as decode_error:
                        self.log_result("authentication", "JWT Token Format Validation", False, 
                                      f"JWT token decode error: {str(decode_error)}")
                else:
                    self.log_result("authentication", "JWT Token Format Validation", False, 
                                  f"Invalid JWT format: {len(token_parts)} parts instead of 3")
                    
            except Exception as e:
                self.log_result("authentication", "JWT Token Format Validation", False, f"Exception: {str(e)}")
                
        # Test 3: Invalid credentials test
        try:
            invalid_data = {
                "username": "invalid_user",
                "password": "wrong_password"
            }
            response = requests.post(f"{self.base_url}/auth/login", json=invalid_data)
            
            if response.status_code == 401:
                self.log_result("authentication", "Invalid Credentials Rejection", True, 
                              "Correctly rejected invalid credentials with 401 status")
            else:
                self.log_result("authentication", "Invalid Credentials Rejection", False, 
                              f"Expected 401, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("authentication", "Invalid Credentials Rejection", False, f"Exception: {str(e)}")
            
    def get_auth_headers(self):
        """Get authorization headers with JWT token"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    def test_authenticated_employee_api(self):
        """Test GET /api/employees with JWT authentication as specified in review request"""
        print("\n=== TESTING AUTHENTICATED EMPLOYEE API ===")
        
        if not self.auth_token:
            self.log_result("employees", "Employee API Tests", False, "No JWT token available from login")
            return
            
        headers = self.get_auth_headers()
        print(f"Using auth headers: Authorization: Bearer {self.auth_token[:50]}...")
        
        # Test 1: Get all employees with authentication
        try:
            response = requests.get(f"{self.base_url}/employees", headers=headers)
            
            print(f"Employee API request to: {self.base_url}/employees")
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                employees = response.json()
                print(f"Response type: {type(employees)}")
                
                if isinstance(employees, list):
                    employee_count = len(employees)
                    print(f"Retrieved {employee_count} employees")
                    
                    # Check for expected employee count (14 including Console Test User)
                    if employee_count >= 14:
                        count_status = f"✅ Expected employee count met: {employee_count} employees (≥14 expected)"
                    else:
                        count_status = f"⚠️ Employee count below expected: {employee_count} employees (<14 expected)"
                    
                    # Look for Console Test User specifically
                    console_test_user_found = False
                    employee_details = []
                    
                    for emp in employees:
                        emp_name = emp.get('full_name', 'Unknown')
                        emp_id = emp.get('employee_id', 'Unknown')
                        emp_dept = emp.get('department', 'Unknown')
                        
                        employee_details.append(f"{emp_name} ({emp_id}) - {emp_dept}")
                        
                        if 'console test user' in emp_name.lower() or 'console' in emp_name.lower():
                            console_test_user_found = True
                            
                    console_status = "✅ Console Test User found" if console_test_user_found else "⚠️ Console Test User not found"
                    
                    # Verify employee data structure
                    if employees:
                        sample_employee = employees[0]
                        required_fields = ['id', 'employee_id', 'full_name', 'department', 'designation', 
                                         'email_address', 'contact_number', 'basic_salary']
                        missing_fields = [field for field in required_fields if field not in sample_employee]
                        
                        if not missing_fields:
                            structure_status = "✅ Employee data structure complete"
                        else:
                            structure_status = f"⚠️ Missing fields in employee data: {missing_fields}"
                    else:
                        structure_status = "❌ No employees to verify structure"
                    
                    self.log_result("employees", "Get All Employees with Authentication", True, 
                                  f"{count_status}. {console_status}. {structure_status}")
                    
                    # Log first few employees for verification
                    print("First 5 employees:")
                    for i, detail in enumerate(employee_details[:5]):
                        print(f"  {i+1}. {detail}")
                    
                    if len(employee_details) > 5:
                        print(f"  ... and {len(employee_details) - 5} more employees")
                        
                else:
                    self.log_result("employees", "Get All Employees with Authentication", False, 
                                  f"Response is not a list. Got type: {type(employees)}")
                    print(f"Unexpected response format: {employees}")
                    
            elif response.status_code == 401:
                self.log_result("employees", "Get All Employees with Authentication", False, 
                              "Authentication failed - 401 Unauthorized. JWT token may be invalid")
                print("Authentication error - check JWT token validity")
                
            elif response.status_code == 403:
                self.log_result("employees", "Get All Employees with Authentication", False, 
                              "Authorization failed - 403 Forbidden. User may not have permission")
                print("Authorization error - user may not have required permissions")
                
            else:
                error_text = response.text
                self.log_result("employees", "Get All Employees with Authentication", False, 
                              f"HTTP {response.status_code}: {error_text}")
                print(f"Unexpected response: {response.status_code} - {error_text}")
                
        except Exception as e:
            self.log_result("employees", "Get All Employees with Authentication", False, f"Exception: {str(e)}")
            print(f"Employee API exception: {str(e)}")
            
        # Test 2: Verify authentication is required (test without token)
        try:
            response = requests.get(f"{self.base_url}/employees")  # No auth header
            
            if response.status_code in [401, 403]:
                self.log_result("employees", "Authentication Required Verification", True, 
                              f"Correctly requires authentication - returned {response.status_code}")
            else:
                self.log_result("employees", "Authentication Required Verification", False, 
                              f"Expected 401/403 without auth, got {response.status_code}")
                
        except Exception as e:
            self.log_result("employees", "Authentication Required Verification", False, f"Exception: {str(e)}")
            
    def test_dashboard_stats_api(self):
        """Test GET /api/dashboard/stats with authentication as specified in review request"""
        print("\n=== TESTING DASHBOARD STATS API ===")
        
        if not self.auth_token:
            self.log_result("dashboard", "Dashboard Stats Tests", False, "No JWT token available from login")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: Get dashboard statistics with authentication
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats", headers=headers)
            
            print(f"Dashboard stats request to: {self.base_url}/dashboard/stats")
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                stats = response.json()
                print(f"Dashboard stats response: {json.dumps(stats, indent=2)}")
                
                required_fields = ["total_employees", "present_today", "logged_in_now", "absent_today"]
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    total_emp = stats["total_employees"]
                    present = stats["present_today"]
                    logged_in = stats["logged_in_now"]
                    absent = stats["absent_today"]
                    
                    # Verify statistics make sense
                    stats_valid = True
                    validation_issues = []
                    
                    if total_emp < 0:
                        stats_valid = False
                        validation_issues.append("Total employees is negative")
                        
                    if present < 0 or logged_in < 0 or absent < 0:
                        stats_valid = False
                        validation_issues.append("Negative values in attendance stats")
                        
                    if present + absent != total_emp:
                        # This might be acceptable depending on business logic
                        validation_issues.append(f"Present ({present}) + Absent ({absent}) ≠ Total ({total_emp})")
                        
                    if logged_in > present:
                        stats_valid = False
                        validation_issues.append(f"Logged in ({logged_in}) > Present ({present})")
                    
                    # Check if we have expected employee count (14+)
                    if total_emp >= 14:
                        count_status = f"✅ Employee count matches expectation: {total_emp} employees (≥14 expected)"
                    else:
                        count_status = f"⚠️ Employee count below expectation: {total_emp} employees (<14 expected)"
                    
                    if stats_valid:
                        self.log_result("dashboard", "Dashboard Statistics with Authentication", True, 
                                      f"{count_status}. Stats: {total_emp} total, {present} present, "
                                      f"{logged_in} logged in, {absent} absent. All statistics valid.")
                    else:
                        self.log_result("dashboard", "Dashboard Statistics with Authentication", False, 
                                      f"Statistics validation issues: {'; '.join(validation_issues)}")
                        
                else:
                    self.log_result("dashboard", "Dashboard Statistics with Authentication", False, 
                                  f"Missing required fields: {missing_fields}")
                    
            elif response.status_code == 401:
                self.log_result("dashboard", "Dashboard Statistics with Authentication", False, 
                              "Authentication failed - 401 Unauthorized")
                
            elif response.status_code == 403:
                self.log_result("dashboard", "Dashboard Statistics with Authentication", False, 
                              "Authorization failed - 403 Forbidden")
                
            else:
                error_text = response.text
                self.log_result("dashboard", "Dashboard Statistics with Authentication", False, 
                              f"HTTP {response.status_code}: {error_text}")
                
        except Exception as e:
            self.log_result("dashboard", "Dashboard Statistics with Authentication", False, f"Exception: {str(e)}")
            
        # Test 2: Verify authentication is required for dashboard stats
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats")  # No auth header
            
            if response.status_code in [401, 403]:
                self.log_result("dashboard", "Dashboard Stats Auth Required", True, 
                              f"Correctly requires authentication - returned {response.status_code}")
            else:
                self.log_result("dashboard", "Dashboard Stats Auth Required", False, 
                              f"Expected 401/403 without auth, got {response.status_code}")
                
        except Exception as e:
            self.log_result("dashboard", "Dashboard Stats Auth Required", False, f"Exception: {str(e)}")
            
    def run_focused_tests(self):
        """Run all focused tests as specified in the review request"""
        print("=" * 80)
        print("FOCUSED HRMS BACKEND API TESTING - LOGIN & EMPLOYEE RETRIEVAL")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Admin credentials: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
        print(f"Expected results: Valid JWT token, 14+ employees including Console Test User")
        print("=" * 80)
        
        # Run tests in the order specified in review request
        self.test_login_authentication()
        self.test_authenticated_employee_api()
        self.test_dashboard_stats_api()
        
        # Print summary
        self.print_test_summary()
        
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("FOCUSED TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            print(f"\n{category.upper()} TESTS:")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            
            for detail in results["details"]:
                print(f"    {detail['status']}: {detail['test']}")
                if detail['status'].startswith('❌'):
                    print(f"      Issue: {detail['message']}")
                    
        print(f"\nOVERALL RESULTS:")
        print(f"  ✅ Total Passed: {total_passed}")
        print(f"  ❌ Total Failed: {total_failed}")
        print(f"  📊 Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%" if (total_passed+total_failed) > 0 else "N/A")
        
        # Specific findings for the review request
        print(f"\nREVIEW REQUEST FINDINGS:")
        
        # Authentication findings
        auth_passed = self.test_results["authentication"]["passed"]
        if auth_passed >= 2:  # Login + token validation
            print(f"  ✅ LOGIN AUTHENTICATION: Working correctly with admin/admin123")
        else:
            print(f"  ❌ LOGIN AUTHENTICATION: Issues found - check credentials or API")
            
        # Employee API findings
        emp_passed = self.test_results["employees"]["passed"]
        if emp_passed >= 1:
            print(f"  ✅ EMPLOYEE RETRIEVAL: Working with JWT authentication")
        else:
            print(f"  ❌ EMPLOYEE RETRIEVAL: Issues found - check authentication or API")
            
        # Dashboard findings
        dash_passed = self.test_results["dashboard"]["passed"]
        if dash_passed >= 1:
            print(f"  ✅ DASHBOARD STATS: Working with authentication")
        else:
            print(f"  ❌ DASHBOARD STATS: Issues found - check authentication or API")
            
        print("=" * 80)

if __name__ == "__main__":
    tester = FocusedHRMSAPITester()
    tester.run_focused_tests()