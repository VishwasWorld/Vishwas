#!/usr/bin/env python3
"""
Comprehensive Employee Creation Testing - Additional Scenarios
"""

import requests
import json
import time

# Configuration
BASE_URL = "https://vishwashrms.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def authenticate():
    """Authenticate and get JWT token"""
    login_data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_additional_employee_scenarios(auth_token):
    """Test additional employee creation scenarios"""
    print("🧪 Testing additional employee creation scenarios...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    test_results = []
    
    # Test 1: Different valid employee data
    timestamp = int(time.time())
    employee_data_1 = {
        "employee_id": f"EMP{timestamp}",
        "full_name": "Rajesh Kumar",
        "department": "Software Development",
        "designation": "Senior Developer",
        "join_date": "2025-01-03T00:00:00Z",
        "contact_number": "+91 9876543211",
        "email_address": f"rajesh.kumar.{timestamp}@vishwasworldtech.com",
        "address": "456 Tech Park, Bangalore",
        "basic_salary": 80000,
        "username": f"rajesh.kumar.{timestamp}",
        "password": "rajesh123"
    }
    
    response = requests.post(f"{BASE_URL}/employees", json=employee_data_1, headers=headers)
    
    if response.status_code == 200:
        created = response.json()
        test_results.append(f"✅ Test 1 PASSED: Created {created['full_name']} (ID: {created['employee_id']})")
    else:
        test_results.append(f"❌ Test 1 FAILED: {response.status_code} - {response.text}")
    
    # Test 2: Different department
    timestamp2 = int(time.time()) + 1
    employee_data_2 = {
        "employee_id": f"EMP{timestamp2}",
        "full_name": "Priya Sharma",
        "department": "Marketing",
        "designation": "Marketing Manager",
        "join_date": "2025-01-03T00:00:00Z",
        "contact_number": "+91 9876543212",
        "email_address": f"priya.sharma.{timestamp2}@vishwasworldtech.com",
        "address": "789 Business District, Bangalore",
        "basic_salary": 65000,
        "username": f"priya.sharma.{timestamp2}",
        "password": "priya123"
    }
    
    response = requests.post(f"{BASE_URL}/employees", json=employee_data_2, headers=headers)
    
    if response.status_code == 200:
        created = response.json()
        test_results.append(f"✅ Test 2 PASSED: Created {created['full_name']} (ID: {created['employee_id']})")
    else:
        test_results.append(f"❌ Test 2 FAILED: {response.status_code} - {response.text}")
    
    # Test 3: With manager field
    timestamp3 = int(time.time()) + 2
    employee_data_3 = {
        "employee_id": f"EMP{timestamp3}",
        "full_name": "Amit Patel",
        "department": "IT",
        "designation": "Junior Developer",
        "join_date": "2025-01-03T00:00:00Z",
        "manager": "Jane Smith",
        "contact_number": "+91 9876543213",
        "email_address": f"amit.patel.{timestamp3}@vishwasworldtech.com",
        "address": "321 Tech Hub, Bangalore",
        "basic_salary": 45000,
        "username": f"amit.patel.{timestamp3}",
        "password": "amit123"
    }
    
    response = requests.post(f"{BASE_URL}/employees", json=employee_data_3, headers=headers)
    
    if response.status_code == 200:
        created = response.json()
        test_results.append(f"✅ Test 3 PASSED: Created {created['full_name']} with manager '{created['manager']}'")
    else:
        test_results.append(f"❌ Test 3 FAILED: {response.status_code} - {response.text}")
    
    return test_results

def test_edge_cases(auth_token):
    """Test edge cases and validation"""
    print("\n🔍 Testing edge cases and validation...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    test_results = []
    
    # Test 1: Duplicate employee ID
    duplicate_data = {
        "employee_id": "EMP101",  # Same as Jane Smith
        "full_name": "Duplicate Employee",
        "department": "IT",
        "designation": "Developer",
        "join_date": "2025-01-03T00:00:00Z",
        "contact_number": "+91 9876543214",
        "email_address": "duplicate@vishwasworldtech.com",
        "address": "Test Address",
        "basic_salary": 50000,
        "username": "duplicate.user",
        "password": "duplicate123"
    }
    
    response = requests.post(f"{BASE_URL}/employees", json=duplicate_data, headers=headers)
    
    if response.status_code == 400 and "already exists" in response.text:
        test_results.append("✅ Duplicate ID validation PASSED: Correctly rejected duplicate employee_id")
    else:
        test_results.append(f"❌ Duplicate ID validation FAILED: Expected 400, got {response.status_code}")
    
    # Test 2: Duplicate username
    timestamp = int(time.time())
    duplicate_username_data = {
        "employee_id": f"EMP{timestamp}",
        "full_name": "Duplicate Username",
        "department": "IT",
        "designation": "Developer",
        "join_date": "2025-01-03T00:00:00Z",
        "contact_number": "+91 9876543215",
        "email_address": f"duplicate.username.{timestamp}@vishwasworldtech.com",
        "address": "Test Address",
        "basic_salary": 50000,
        "username": "jane.smith",  # Same as Jane Smith
        "password": "duplicate123"
    }
    
    response = requests.post(f"{BASE_URL}/employees", json=duplicate_username_data, headers=headers)
    
    if response.status_code == 400 and "already exists" in response.text:
        test_results.append("✅ Duplicate username validation PASSED: Correctly rejected duplicate username")
    else:
        test_results.append(f"❌ Duplicate username validation FAILED: Expected 400, got {response.status_code}")
    
    # Test 3: Missing required fields (should fail with 422)
    incomplete_data = {
        "employee_id": "EMP_INCOMPLETE2",
        "full_name": "Incomplete Employee",
        "department": "IT",
        # Missing other required fields
    }
    
    response = requests.post(f"{BASE_URL}/employees", json=incomplete_data, headers=headers)
    
    if response.status_code == 422:
        test_results.append("✅ Missing fields validation PASSED: Correctly rejected incomplete data")
    else:
        test_results.append(f"❌ Missing fields validation FAILED: Expected 422, got {response.status_code}")
    
    return test_results

def test_employee_retrieval(auth_token):
    """Test employee retrieval endpoints"""
    print("\n📋 Testing employee retrieval endpoints...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    test_results = []
    
    # Test 1: Get all employees
    response = requests.get(f"{BASE_URL}/employees", headers=headers)
    
    if response.status_code == 200:
        employees = response.json()
        test_results.append(f"✅ Get all employees PASSED: Retrieved {len(employees)} employees")
        
        # Check if Jane Smith is in the list
        jane_found = any(emp.get("full_name") == "Jane Smith" for emp in employees)
        if jane_found:
            test_results.append("✅ Jane Smith found in employee list")
        else:
            test_results.append("❌ Jane Smith not found in employee list")
    else:
        test_results.append(f"❌ Get all employees FAILED: {response.status_code}")
    
    # Test 2: Get specific employee (Jane Smith)
    response = requests.get(f"{BASE_URL}/employees/EMP101", headers=headers)
    
    if response.status_code == 200:
        employee = response.json()
        if employee.get("full_name") == "Jane Smith":
            test_results.append(f"✅ Get specific employee PASSED: Retrieved {employee['full_name']}")
        else:
            test_results.append(f"❌ Get specific employee FAILED: Wrong employee data")
    else:
        test_results.append(f"❌ Get specific employee FAILED: {response.status_code}")
    
    # Test 3: Get non-existent employee
    response = requests.get(f"{BASE_URL}/employees/NONEXISTENT", headers=headers)
    
    if response.status_code == 404:
        test_results.append("✅ Non-existent employee PASSED: Correctly returned 404")
    else:
        test_results.append(f"❌ Non-existent employee FAILED: Expected 404, got {response.status_code}")
    
    return test_results

def main():
    print("🚀 COMPREHENSIVE EMPLOYEE CREATION TESTING")
    print("=" * 60)
    
    # Authenticate
    auth_token = authenticate()
    if not auth_token:
        print("❌ Authentication failed")
        return
    
    print("✅ Authenticated successfully")
    
    # Run all tests
    additional_tests = test_additional_employee_scenarios(auth_token)
    edge_case_tests = test_edge_cases(auth_token)
    retrieval_tests = test_employee_retrieval(auth_token)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    all_tests = additional_tests + edge_case_tests + retrieval_tests
    
    for result in all_tests:
        print(result)
    
    passed = sum(1 for result in all_tests if result.startswith("✅"))
    failed = len(all_tests) - passed
    
    print(f"\n📈 OVERALL RESULTS: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Employee creation functionality is working perfectly")
        print("✅ All validation and edge cases handled correctly")
    else:
        print(f"\n⚠️  {failed} tests failed - review needed")

if __name__ == "__main__":
    main()