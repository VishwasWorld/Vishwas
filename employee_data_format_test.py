#!/usr/bin/env python3
"""
Employee Data Format Analysis Test
Focused test to analyze the exact format of employee data returned by GET /api/employees endpoint
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://vishwashrms.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class EmployeeDataFormatTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print("=== AUTHENTICATING ===")
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
                    print("❌ Authentication response missing access_token")
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
        
    def analyze_employee_data_format(self):
        """Analyze the exact format of employee data returned by GET /api/employees"""
        print("\n=== EMPLOYEE DATA FORMAT ANALYSIS ===")
        
        if not self.auth_token:
            print("❌ No authentication token available")
            return
            
        headers = self.get_auth_headers()
        
        try:
            print("🔍 Testing GET /api/employees endpoint...")
            response = requests.get(f"{self.base_url}/employees", headers=headers)
            
            if response.status_code == 200:
                employees = response.json()
                
                print(f"✅ Successfully retrieved employee data")
                print(f"📊 Total employees returned: {len(employees)}")
                
                if len(employees) == 0:
                    print("⚠️  No employees found in database")
                    return
                    
                print("\n=== EMPLOYEE COUNT AND NAMES ===")
                for i, emp in enumerate(employees, 1):
                    emp_name = emp.get('full_name', 'Unknown')
                    emp_id = emp.get('employee_id', 'Unknown')
                    print(f"{i}. {emp_name} (ID: {emp_id})")
                
                # Check for recently created employees
                print("\n=== CHECKING FOR RECENTLY CREATED EMPLOYEES ===")
                jane_smith_found = False
                emp101_found = False
                
                for emp in employees:
                    if 'Jane Smith' in emp.get('full_name', ''):
                        jane_smith_found = True
                        print(f"✅ Found Jane Smith: {emp.get('full_name')} (ID: {emp.get('employee_id')})")
                    if emp.get('employee_id') == 'EMP101':
                        emp101_found = True
                        print(f"✅ Found EMP101: {emp.get('full_name')} (ID: {emp.get('employee_id')})")
                
                if not jane_smith_found:
                    print("❌ Jane Smith not found in employee list")
                if not emp101_found:
                    print("❌ EMP101 not found in employee list")
                
                # Analyze field structure of first employee
                print("\n=== FIELD STRUCTURE ANALYSIS ===")
                if employees:
                    sample_employee = employees[0]
                    print(f"📋 Analyzing structure of employee: {sample_employee.get('full_name', 'Unknown')}")
                    print(f"🔑 Employee ID: {sample_employee.get('employee_id', 'Missing')}")
                    
                    # Check for React key field
                    print("\n=== REACT KEY FIELD ANALYSIS ===")
                    if 'id' in sample_employee:
                        print(f"✅ 'id' field found: {sample_employee['id']}")
                        print("✅ This can be used as React key")
                    else:
                        print("❌ 'id' field NOT found")
                        
                    if 'employee_id' in sample_employee:
                        print(f"✅ 'employee_id' field found: {sample_employee['employee_id']}")
                        print("✅ This can be used as React key alternative")
                    else:
                        print("❌ 'employee_id' field NOT found")
                    
                    # Document all fields
                    print("\n=== COMPLETE FIELD STRUCTURE ===")
                    print("All fields in employee object:")
                    for field_name, field_value in sample_employee.items():
                        field_type = type(field_value).__name__
                        if isinstance(field_value, str) and len(field_value) > 50:
                            display_value = field_value[:50] + "..."
                        else:
                            display_value = field_value
                        print(f"  • {field_name}: {display_value} (type: {field_type})")
                    
                    # Check field consistency across all employees
                    print("\n=== FIELD CONSISTENCY CHECK ===")
                    all_fields = set()
                    for emp in employees:
                        all_fields.update(emp.keys())
                    
                    print(f"📊 Total unique fields across all employees: {len(all_fields)}")
                    
                    # Check if all employees have the same fields
                    field_consistency = {}
                    for field in all_fields:
                        count = sum(1 for emp in employees if field in emp)
                        field_consistency[field] = count
                        
                    print("\nField presence across employees:")
                    for field, count in sorted(field_consistency.items()):
                        percentage = (count / len(employees)) * 100
                        status = "✅" if count == len(employees) else "⚠️"
                        print(f"  {status} {field}: {count}/{len(employees)} ({percentage:.1f}%)")
                    
                    # Analyze data types
                    print("\n=== DATA TYPE ANALYSIS ===")
                    type_analysis = {}
                    for emp in employees:
                        for field, value in emp.items():
                            field_type = type(value).__name__
                            if field not in type_analysis:
                                type_analysis[field] = {}
                            if field_type not in type_analysis[field]:
                                type_analysis[field][field_type] = 0
                            type_analysis[field][field_type] += 1
                    
                    for field, types in sorted(type_analysis.items()):
                        if len(types) == 1:
                            type_name = list(types.keys())[0]
                            print(f"  ✅ {field}: {type_name} (consistent)")
                        else:
                            print(f"  ⚠️  {field}: mixed types - {types}")
                    
                    # Check for missing or unexpected fields for frontend compatibility
                    print("\n=== FRONTEND COMPATIBILITY CHECK ===")
                    expected_fields = [
                        'id', 'employee_id', 'full_name', 'department', 'designation',
                        'email_address', 'contact_number', 'basic_salary', 'join_date', 'status'
                    ]
                    
                    missing_fields = []
                    present_fields = []
                    
                    for field in expected_fields:
                        if field in sample_employee:
                            present_fields.append(field)
                        else:
                            missing_fields.append(field)
                    
                    if present_fields:
                        print("✅ Present expected fields:")
                        for field in present_fields:
                            print(f"    • {field}")
                    
                    if missing_fields:
                        print("❌ Missing expected fields:")
                        for field in missing_fields:
                            print(f"    • {field}")
                    
                    # Additional fields not in expected list
                    additional_fields = [field for field in sample_employee.keys() if field not in expected_fields]
                    if additional_fields:
                        print("ℹ️  Additional fields (not in expected list):")
                        for field in additional_fields:
                            print(f"    • {field}")
                    
                    # Summary for React key usage
                    print("\n=== REACT KEY RECOMMENDATION ===")
                    if 'id' in sample_employee:
                        print("✅ RECOMMENDED: Use 'id' field as React key")
                        print(f"   Example: key={{employee.id}} // Value: {sample_employee['id']}")
                    elif 'employee_id' in sample_employee:
                        print("✅ ALTERNATIVE: Use 'employee_id' field as React key")
                        print(f"   Example: key={{employee.employee_id}} // Value: {sample_employee['employee_id']}")
                    else:
                        print("❌ WARNING: No suitable field found for React key")
                        print("   Consider using array index as fallback (not recommended)")
                
                # Raw JSON sample for reference
                print("\n=== RAW JSON SAMPLE ===")
                if employees:
                    print("First employee raw JSON:")
                    print(json.dumps(employees[0], indent=2, default=str))
                
            else:
                print(f"❌ Failed to retrieve employees: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception during employee data analysis: {str(e)}")

def main():
    """Main test execution"""
    print("🚀 Starting Employee Data Format Analysis")
    print("=" * 60)
    
    tester = EmployeeDataFormatTester()
    
    # Step 1: Authenticate
    if not tester.authenticate():
        print("❌ Authentication failed. Cannot proceed with testing.")
        return
    
    # Step 2: Analyze employee data format
    tester.analyze_employee_data_format()
    
    print("\n" + "=" * 60)
    print("🏁 Employee Data Format Analysis Complete")

if __name__ == "__main__":
    main()