#!/usr/bin/env python3
"""
Employee Creation API Testing - Focused on 422 Validation Error Analysis
Tests the specific employee creation issue mentioned in the review request
"""

import requests
import json
from datetime import datetime, timezone
import time

# Configuration
BASE_URL = "https://vishwashrms.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class EmployeeCreationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print("=== AUTHENTICATING WITH ADMIN CREDENTIALS ===")
        
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
                    print(f"❌ Authentication failed: Missing access_token in response")
                    return False
            else:
                print(f"❌ Authentication failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication exception: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    def check_backend_logs(self):
        """Check backend logs for errors"""
        print("\n=== CHECKING BACKEND LOGS ===")
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '50', '/var/log/supervisor/backend.err.log'], 
                                  capture_output=True, text=True)
            if result.stdout:
                print("Backend Error Logs (last 50 lines):")
                print(result.stdout)
            else:
                print("No recent backend error logs found")
        except Exception as e:
            print(f"Could not read backend logs: {str(e)}")
    
    def analyze_employee_model(self):
        """Analyze the backend employee model requirements"""
        print("\n=== ANALYZING BACKEND EMPLOYEE MODEL ===")
        
        # Based on the server.py code, here are the required fields for EmployeeCreate:
        backend_model_fields = {
            "employee_id": "str",
            "full_name": "str", 
            "department": "str",
            "designation": "str",
            "join_date": "datetime",
            "manager": "str (optional, default='')",
            "contact_number": "str",
            "email_address": "str",
            "address": "str",
            "basic_salary": "float",
            "username": "str",
            "password": "str"
        }
        
        print("Backend EmployeeCreate model requires these fields:")
        for field, field_type in backend_model_fields.items():
            print(f"  - {field}: {field_type}")
        
        return backend_model_fields
    
    def test_employee_creation_with_review_data(self):
        """Test employee creation with the exact data from review request"""
        print("\n=== TESTING EMPLOYEE CREATION WITH REVIEW REQUEST DATA ===")
        
        if not self.auth_token:
            print("❌ No authentication token available")
            return False
            
        headers = self.get_auth_headers()
        
        # Exact data from review request
        employee_data = {
            "full_name": "Test Employee",
            "employee_id": "EMP999",
            "email_address": "test@vishwasworldtech.com",
            "contact_number": "+91 9876543210",
            "department": "IT",
            "designation": "Software Engineer",
            "address": "123 Test Street, Bangalore",
            "basic_salary": 50000,
            "join_date": "2025-01-03",
            "status": "Active"
        }
        
        print("Testing with review request data:")
        print(json.dumps(employee_data, indent=2))
        
        try:
            response = requests.post(f"{self.base_url}/employees", json=employee_data, headers=headers)
            
            print(f"\nResponse Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 422:
                print("❌ 422 VALIDATION ERROR DETECTED!")
                try:
                    error_data = response.json()
                    print("Validation Error Details:")
                    print(json.dumps(error_data, indent=2))
                    
                    # Analyze the specific validation errors
                    if "detail" in error_data:
                        print("\nDetailed Validation Errors:")
                        for error in error_data["detail"]:
                            if isinstance(error, dict):
                                field = error.get("loc", ["unknown"])[-1] if error.get("loc") else "unknown"
                                message = error.get("msg", "No message")
                                error_type = error.get("type", "unknown")
                                print(f"  - Field '{field}': {message} (type: {error_type})")
                            else:
                                print(f"  - {error}")
                                
                except Exception as e:
                    print(f"Could not parse error response: {str(e)}")
                    print(f"Raw response: {response.text}")
                    
            elif response.status_code == 200:
                print("✅ Employee creation successful!")
                data = response.json()
                print(f"Created employee: {data.get('full_name', 'Unknown')} (ID: {data.get('employee_id', 'Unknown')})")
                
            else:
                print(f"❌ Unexpected response code: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception during employee creation: {str(e)}")
            
        return response.status_code == 200
    
    def test_with_missing_fields(self):
        """Test what happens when required fields are missing"""
        print("\n=== TESTING WITH MISSING REQUIRED FIELDS ===")
        
        if not self.auth_token:
            print("❌ No authentication token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test with missing username and password (required by backend model)
        incomplete_data = {
            "full_name": "Test Employee",
            "employee_id": "EMP998",
            "email_address": "test2@vishwasworldtech.com",
            "contact_number": "+91 9876543211",
            "department": "IT",
            "designation": "Software Engineer",
            "address": "123 Test Street, Bangalore",
            "basic_salary": 50000,
            "join_date": "2025-01-03T00:00:00Z"
            # Missing: username, password, manager (optional)
        }
        
        print("Testing with missing username and password:")
        print(json.dumps(incomplete_data, indent=2))
        
        try:
            response = requests.post(f"{self.base_url}/employees", json=incomplete_data, headers=headers)
            
            print(f"\nResponse Status Code: {response.status_code}")
            
            if response.status_code == 422:
                error_data = response.json()
                print("Missing Field Validation Errors:")
                print(json.dumps(error_data, indent=2))
            else:
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    def test_with_correct_backend_format(self):
        """Test with data formatted according to backend model requirements"""
        print("\n=== TESTING WITH CORRECT BACKEND MODEL FORMAT ===")
        
        if not self.auth_token:
            print("❌ No authentication token available")
            return
            
        headers = self.get_auth_headers()
        
        # Data formatted according to EmployeeCreate model from server.py
        correct_employee_data = {
            "employee_id": "EMP997",
            "full_name": "Test Employee Corrected",
            "department": "IT",
            "designation": "Software Engineer", 
            "join_date": "2025-01-03T00:00:00Z",  # ISO format datetime
            "manager": "Tech Lead",  # Optional but included
            "contact_number": "+91 9876543212",
            "email_address": "testcorrected@vishwasworldtech.com",
            "address": "123 Test Street, Bangalore",
            "basic_salary": 50000.0,  # Explicit float
            "username": f"testuser_{int(time.time())}",  # Required field
            "password": "testpass123"  # Required field
        }
        
        print("Testing with correct backend model format:")
        print(json.dumps(correct_employee_data, indent=2))
        
        try:
            response = requests.post(f"{self.base_url}/employees", json=correct_employee_data, headers=headers)
            
            print(f"\nResponse Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Employee creation successful with correct format!")
                data = response.json()
                print(f"Created employee: {data.get('full_name', 'Unknown')} (ID: {data.get('employee_id', 'Unknown')})")
                return True
            elif response.status_code == 422:
                error_data = response.json()
                print("❌ Still getting validation errors:")
                print(json.dumps(error_data, indent=2))
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            
        return False
    
    def test_data_type_issues(self):
        """Test for data type issues"""
        print("\n=== TESTING FOR DATA TYPE ISSUES ===")
        
        if not self.auth_token:
            print("❌ No authentication token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test with various data type variations
        test_cases = [
            {
                "name": "String salary instead of float",
                "data": {
                    "employee_id": "EMP996",
                    "full_name": "Test Employee String Salary",
                    "department": "IT",
                    "designation": "Software Engineer",
                    "join_date": "2025-01-03T00:00:00Z",
                    "manager": "Tech Lead",
                    "contact_number": "+91 9876543213",
                    "email_address": "teststring@vishwasworldtech.com",
                    "address": "123 Test Street, Bangalore",
                    "basic_salary": "50000",  # String instead of float
                    "username": f"teststring_{int(time.time())}",
                    "password": "testpass123"
                }
            },
            {
                "name": "Date string without time",
                "data": {
                    "employee_id": "EMP995",
                    "full_name": "Test Employee Date Format",
                    "department": "IT", 
                    "designation": "Software Engineer",
                    "join_date": "2025-01-03",  # Date without time
                    "manager": "Tech Lead",
                    "contact_number": "+91 9876543214",
                    "email_address": "testdate@vishwasworldtech.com",
                    "address": "123 Test Street, Bangalore",
                    "basic_salary": 50000.0,
                    "username": f"testdate_{int(time.time())}",
                    "password": "testpass123"
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n--- Testing: {test_case['name']} ---")
            print(json.dumps(test_case['data'], indent=2))
            
            try:
                response = requests.post(f"{self.base_url}/employees", json=test_case['data'], headers=headers)
                
                print(f"Response Status Code: {response.status_code}")
                
                if response.status_code == 422:
                    error_data = response.json()
                    print("Validation Errors:")
                    print(json.dumps(error_data, indent=2))
                elif response.status_code == 200:
                    print("✅ Success!")
                    data = response.json()
                    print(f"Created: {data.get('full_name', 'Unknown')}")
                else:
                    print(f"Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
    
    def compare_frontend_backend_fields(self):
        """Compare frontend form fields with backend requirements"""
        print("\n=== COMPARING FRONTEND VS BACKEND FIELD REQUIREMENTS ===")
        
        # Fields from review request (likely frontend form fields)
        frontend_fields = {
            "full_name": "Test Employee",
            "employee_id": "EMP999", 
            "email_address": "test@vishwasworldtech.com",
            "contact_number": "+91 9876543210",
            "department": "IT",
            "designation": "Software Engineer", 
            "address": "123 Test Street, Bangalore",
            "basic_salary": 50000,
            "join_date": "2025-01-03",
            "status": "Active"
        }
        
        # Backend required fields (from EmployeeCreate model)
        backend_required_fields = {
            "employee_id": "str",
            "full_name": "str",
            "department": "str", 
            "designation": "str",
            "join_date": "datetime",
            "manager": "str (optional)",
            "contact_number": "str",
            "email_address": "str", 
            "address": "str",
            "basic_salary": "float",
            "username": "str (REQUIRED)",
            "password": "str (REQUIRED)"
        }
        
        print("Frontend form fields:")
        for field, value in frontend_fields.items():
            print(f"  ✓ {field}: {type(value).__name__}")
            
        print("\nBackend required fields:")
        for field, field_type in backend_required_fields.items():
            print(f"  • {field}: {field_type}")
            
        print("\nField Analysis:")
        
        # Check for missing required fields
        missing_in_frontend = []
        for backend_field in backend_required_fields.keys():
            if backend_field not in frontend_fields and "optional" not in backend_required_fields[backend_field]:
                missing_in_frontend.append(backend_field)
                
        if missing_in_frontend:
            print("❌ MISSING REQUIRED FIELDS IN FRONTEND DATA:")
            for field in missing_in_frontend:
                print(f"  - {field}: {backend_required_fields[field]}")
        else:
            print("✅ All required backend fields present in frontend data")
            
        # Check for extra fields in frontend
        extra_in_frontend = []
        for frontend_field in frontend_fields.keys():
            if frontend_field not in backend_required_fields:
                extra_in_frontend.append(frontend_field)
                
        if extra_in_frontend:
            print("⚠️  EXTRA FIELDS IN FRONTEND DATA (not in backend model):")
            for field in extra_in_frontend:
                print(f"  - {field}: {frontend_fields[field]}")
        
        # Check data types
        print("\nData Type Analysis:")
        type_issues = []
        
        if "basic_salary" in frontend_fields:
            if not isinstance(frontend_fields["basic_salary"], float):
                type_issues.append(f"basic_salary: frontend sends {type(frontend_fields['basic_salary']).__name__}, backend expects float")
                
        if "join_date" in frontend_fields:
            if isinstance(frontend_fields["join_date"], str) and "T" not in frontend_fields["join_date"]:
                type_issues.append(f"join_date: frontend sends date string '{frontend_fields['join_date']}', backend expects datetime with time")
                
        if type_issues:
            print("❌ POTENTIAL DATA TYPE ISSUES:")
            for issue in type_issues:
                print(f"  - {issue}")
        else:
            print("✅ No obvious data type issues detected")
    
    def run_comprehensive_test(self):
        """Run all tests to identify the employee creation issue"""
        print("🔍 COMPREHENSIVE EMPLOYEE CREATION API TESTING")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return
            
        # Step 2: Analyze backend model
        self.analyze_employee_model()
        
        # Step 3: Compare frontend vs backend requirements
        self.compare_frontend_backend_fields()
        
        # Step 4: Test with review request data (likely to fail)
        success1 = self.test_employee_creation_with_review_data()
        
        # Step 5: Test with missing fields
        self.test_with_missing_fields()
        
        # Step 6: Test data type issues
        self.test_data_type_issues()
        
        # Step 7: Test with correct backend format
        success2 = self.test_with_correct_backend_format()
        
        # Step 8: Check backend logs
        self.check_backend_logs()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 TESTING SUMMARY & DIAGNOSIS")
        print("=" * 60)
        
        if success1:
            print("✅ Review request data worked - no issue found")
        elif success2:
            print("❌ Review request data failed, but corrected format worked")
            print("🔍 ROOT CAUSE: Missing required fields (username, password) or data type issues")
        else:
            print("❌ Both tests failed - deeper investigation needed")
            
        print("\n🔧 RECOMMENDED FIXES:")
        print("1. Add 'username' and 'password' fields to frontend form")
        print("2. Ensure 'basic_salary' is sent as number, not string")
        print("3. Send 'join_date' in ISO datetime format (YYYY-MM-DDTHH:MM:SSZ)")
        print("4. Remove 'status' field from frontend (not in backend model)")
        print("5. Add optional 'manager' field to frontend form")

if __name__ == "__main__":
    tester = EmployeeCreationTester()
    tester.run_comprehensive_test()