#!/usr/bin/env python3
"""
Comprehensive HRMS Backend API Testing Suite
Additional edge case testing for the Vishwas World Tech HRMS system
"""

import requests
import json
from datetime import datetime, timezone
import time

# Configuration
BASE_URL = "https://vishwas-hrms.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_edge_cases():
    """Test edge cases and error handling"""
    print("🔍 Running Comprehensive Edge Case Tests")
    print("=" * 60)
    
    # Get auth token
    login_data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print("❌ Failed to get auth token")
        return False
        
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Authentication successful")
    
    # Test 1: Duplicate employee creation
    print("\n--- Testing Duplicate Employee Creation ---")
    duplicate_employee = {
        "employee_id": "VWT001",  # This already exists (admin)
        "full_name": "Duplicate User",
        "department": "IT",
        "designation": "Developer",
        "join_date": "2024-01-01T00:00:00Z",
        "contact_number": "+91-1234567890",
        "email_address": "duplicate@test.com",
        "address": "Test Address",
        "basic_salary": 50000.0,
        "username": "duplicate_user",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/employees", json=duplicate_employee, headers=headers)
    if response.status_code == 400:
        print("✅ Correctly rejected duplicate employee ID")
    else:
        print(f"❌ Expected 400, got {response.status_code}")
        
    # Test 2: Invalid employee lookup
    print("\n--- Testing Invalid Employee Lookup ---")
    response = requests.get(f"{BASE_URL}/employees/NONEXISTENT", headers=headers)
    if response.status_code == 404:
        print("✅ Correctly returned 404 for non-existent employee")
    else:
        print(f"❌ Expected 404, got {response.status_code}")
        
    # Test 3: Double login attempt
    print("\n--- Testing Double Login Attempt ---")
    login_data = {
        "employee_id": "VWT001",
        "location": {
            "latitude": 12.9716,
            "longitude": 77.5946,
            "address": "Office Location"
        }
    }
    
    # First login
    response1 = requests.post(f"{BASE_URL}/attendance/login", json=login_data, headers=headers)
    # Second login attempt
    response2 = requests.post(f"{BASE_URL}/attendance/login", json=login_data, headers=headers)
    
    if response1.status_code == 200 and response2.status_code == 400:
        print("✅ Correctly prevented double login")
    else:
        print(f"❌ Double login handling failed: {response1.status_code}, {response2.status_code}")
        
    # Test 4: Logout without login
    print("\n--- Testing Logout Without Login ---")
    logout_data = {
        "employee_id": "EMP999",  # Non-existent employee
        "location": {
            "latitude": 12.9716,
            "longitude": 77.5946,
            "address": "Office Location"
        }
    }
    
    response = requests.post(f"{BASE_URL}/attendance/logout", json=logout_data, headers=headers)
    if response.status_code == 404:
        print("✅ Correctly handled logout without login")
    else:
        print(f"❌ Expected 404, got {response.status_code}")
        
    # Test 5: Invalid JWT token
    print("\n--- Testing Invalid JWT Token ---")
    invalid_headers = {"Authorization": "Bearer invalid_token_here"}
    response = requests.get(f"{BASE_URL}/employees", headers=invalid_headers)
    if response.status_code == 401:
        print("✅ Correctly rejected invalid JWT token")
    else:
        print(f"❌ Expected 401, got {response.status_code}")
        
    # Test 6: Missing authorization header
    print("\n--- Testing Missing Authorization ---")
    response = requests.get(f"{BASE_URL}/dashboard/stats")  # No headers
    if response.status_code in [401, 403]:
        print("✅ Correctly required authorization")
    else:
        print(f"❌ Expected 401/403, got {response.status_code}")
        
    print("\n" + "=" * 60)
    print("🎯 Edge Case Testing Complete")
    return True

def test_data_validation():
    """Test data validation and constraints"""
    print("\n🔍 Testing Data Validation")
    print("=" * 60)
    
    # Get auth token
    login_data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test invalid employee data
    print("\n--- Testing Invalid Employee Data ---")
    invalid_employee = {
        "employee_id": "",  # Empty ID
        "full_name": "",    # Empty name
        "department": "IT",
        "designation": "Developer",
        "join_date": "invalid-date",  # Invalid date
        "contact_number": "+91-1234567890",
        "email_address": "invalid-email",  # Invalid email format
        "address": "Test Address",
        "basic_salary": -1000.0,  # Negative salary
        "username": "",  # Empty username
        "password": "123"  # Too short password
    }
    
    response = requests.post(f"{BASE_URL}/employees", json=invalid_employee, headers=headers)
    if response.status_code == 422:  # Validation error
        print("✅ Correctly validated employee data")
    else:
        print(f"❌ Expected 422 validation error, got {response.status_code}")
        
    # Test invalid attendance data
    print("\n--- Testing Invalid Attendance Data ---")
    invalid_attendance = {
        "employee_id": "",  # Empty employee ID
        "location": {}  # Empty location
    }
    
    response = requests.post(f"{BASE_URL}/attendance/login", json=invalid_attendance, headers=headers)
    if response.status_code in [400, 422]:
        print("✅ Correctly validated attendance data")
    else:
        print(f"❌ Expected 400/422, got {response.status_code}")
        
    print("\n" + "=" * 60)
    print("🎯 Data Validation Testing Complete")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive HRMS Backend Tests")
    test_edge_cases()
    test_data_validation()
    print("\n✅ All comprehensive tests completed!")