#!/usr/bin/env python3
"""
Test the FIXED employee creation functionality with the exact data from review request
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
    print("🔐 Authenticating...")
    
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully authenticated as {data['employee']['full_name']}")
        return data["access_token"]
    else:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return None

def test_employee_creation_with_review_data(auth_token):
    """Test employee creation with exact data from review request"""
    print("\n🧪 Testing employee creation with EXACT review request data...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Exact data from review request
    employee_data = {
        "employee_id": "EMP101",
        "full_name": "Jane Smith",
        "department": "IT", 
        "designation": "Senior Developer",
        "join_date": "2025-01-03T00:00:00Z",
        "contact_number": "+91 9876543210",
        "email_address": "jane.smith@vishwasworldtech.com",
        "address": "123 Test Street, Bangalore",
        "basic_salary": 75000,
        "username": "jane.smith",
        "password": "temppass123"
    }
    
    print(f"📤 Sending employee data:")
    print(json.dumps(employee_data, indent=2))
    
    response = requests.post(f"{BASE_URL}/employees", json=employee_data, headers=headers)
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"📥 Response Body: {response.text}")
    
    if response.status_code == 200:
        created_employee = response.json()
        print(f"\n✅ SUCCESS: Employee creation FIXED!")
        print(f"✅ Created employee: {created_employee['full_name']} (ID: {created_employee['employee_id']})")
        print(f"✅ The 422 validation error is RESOLVED!")
        return True, created_employee
        
    elif response.status_code == 422:
        error_data = response.json()
        print(f"\n❌ FAILED: 422 validation error still exists!")
        print(f"❌ Error details: {json.dumps(error_data, indent=2)}")
        return False, error_data
        
    elif response.status_code == 400:
        error_data = response.json()
        if "already exists" in error_data.get("detail", "").lower():
            print(f"\n⚠️  Employee already exists, trying with different ID...")
            # Try with different ID
            timestamp = int(time.time())
            employee_data["employee_id"] = f"EMP{timestamp}"
            employee_data["username"] = f"jane.smith.{timestamp}"
            employee_data["email_address"] = f"jane.smith.{timestamp}@vishwasworldtech.com"
            
            response = requests.post(f"{BASE_URL}/employees", json=employee_data, headers=headers)
            
            if response.status_code == 200:
                created_employee = response.json()
                print(f"✅ SUCCESS: Employee creation FIXED!")
                print(f"✅ Created employee: {created_employee['full_name']} (ID: {created_employee['employee_id']})")
                return True, created_employee
            else:
                print(f"❌ Still failed: {response.status_code} - {response.text}")
                return False, response.json()
        else:
            print(f"\n❌ FAILED: {response.status_code} - {error_data}")
            return False, error_data
    else:
        print(f"\n❌ FAILED: Unexpected status {response.status_code} - {response.text}")
        return False, {"error": response.text}

def test_employee_list(auth_token):
    """Test that created employee appears in employee list"""
    print("\n📋 Testing employee list retrieval...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = requests.get(f"{BASE_URL}/employees", headers=headers)
    
    if response.status_code == 200:
        employees = response.json()
        print(f"✅ Retrieved {len(employees)} employees from database")
        
        # Look for Jane Smith
        jane_found = any(emp.get("full_name") == "Jane Smith" for emp in employees)
        if jane_found:
            print("✅ Jane Smith found in employee list")
        else:
            print("⚠️  Jane Smith not found (may have different ID)")
            
        return True
    else:
        print(f"❌ Failed to retrieve employee list: {response.status_code}")
        return False

def test_validation_still_works(auth_token):
    """Test that validation still works for missing fields"""
    print("\n🔍 Testing validation for missing required fields...")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test with missing username and password
    incomplete_data = {
        "employee_id": "EMP_INCOMPLETE",
        "full_name": "Incomplete Employee",
        "department": "IT",
        "designation": "Developer",
        "join_date": "2025-01-03T00:00:00Z",
        "contact_number": "+91 9876543212",
        "email_address": "incomplete@vishwasworldtech.com",
        "address": "Test Address",
        "basic_salary": 50000,
        # Missing username and password intentionally
    }
    
    response = requests.post(f"{BASE_URL}/employees", json=incomplete_data, headers=headers)
    
    if response.status_code == 422:
        print("✅ Validation correctly rejects incomplete data")
        return True
    else:
        print(f"❌ Expected 422 for incomplete data, got {response.status_code}")
        return False

def main():
    print("🚀 TESTING FIXED EMPLOYEE CREATION FUNCTIONALITY")
    print("=" * 60)
    
    # Step 1: Authenticate
    auth_token = authenticate()
    if not auth_token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Test main employee creation with review data
    success, result = test_employee_creation_with_review_data(auth_token)
    
    # Step 3: Test employee list retrieval
    test_employee_list(auth_token)
    
    # Step 4: Test validation still works
    test_validation_still_works(auth_token)
    
    # Final result
    print("\n" + "=" * 60)
    print("📊 FINAL RESULT")
    print("=" * 60)
    
    if success:
        print("🎉 EMPLOYEE CREATION FIX VERIFICATION: SUCCESS")
        print("✅ The 422 validation error has been RESOLVED")
        print("✅ Employee creation API now accepts complete required fields")
        print("✅ Backend properly processes username and password fields")
    else:
        print("❌ EMPLOYEE CREATION FIX VERIFICATION: FAILED")
        print("❌ The 422 validation error still exists")
        print("❌ Frontend is still missing required username/password fields")
        
    return success

if __name__ == "__main__":
    main()