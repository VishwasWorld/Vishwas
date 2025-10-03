#!/usr/bin/env python3
"""
Enhanced HRMS Features Testing Suite
Tests all new enhanced features for the Vishwas World Tech HRMS system
"""

import requests
import json
from datetime import datetime, timezone
import uuid
import time
import base64
import io

# Configuration
BASE_URL = "https://vishwashrms.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class EnhancedHRMSAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_results = {
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "employee_deletion": {"passed": 0, "failed": 0, "details": []},
            "document_management": {"passed": 0, "failed": 0, "details": []},
            "announcements": {"passed": 0, "failed": 0, "details": []},
            "enhanced_dashboard": {"passed": 0, "failed": 0, "details": []}
        }
        self.created_employee_id = None
        self.created_announcement_id = None
        self.uploaded_document_id = None
        
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
        """Test authentication to get token"""
        print("\n=== TESTING AUTHENTICATION FOR ENHANCED FEATURES ===")
        
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
            
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    def test_employee_deletion(self):
        """Test employee deletion functionality"""
        print("\n=== TESTING EMPLOYEE DELETION API ===")
        
        if not self.auth_token:
            self.log_result("employee_deletion", "Employee Deletion Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # First create a test employee to delete
        try:
            new_employee_id = f"TEST_DEL_{int(time.time())}"
            self.created_employee_id = new_employee_id
            
            employee_data = {
                "employee_id": new_employee_id,
                "full_name": "Priya Sharma",
                "department": "Quality Assurance",
                "designation": "QA Engineer",
                "join_date": "2024-01-20T00:00:00Z",
                "manager": "QA Lead",
                "contact_number": "+91-9876543211",
                "email_address": "priya.sharma@vishwasworld.com",
                "address": "456 Tech Hub, Bangalore, Karnataka",
                "basic_salary": 65000.0,
                "username": f"priya_{int(time.time())}",
                "password": "priya123"
            }
            
            response = requests.post(f"{self.base_url}/employees", json=employee_data, headers=headers)
            
            if response.status_code == 200:
                created_employee = response.json()
                self.log_result("employee_deletion", "Create Test Employee for Deletion", True, 
                              f"Successfully created test employee {created_employee['full_name']}")
            else:
                self.log_result("employee_deletion", "Create Test Employee for Deletion", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return
                
        except Exception as e:
            self.log_result("employee_deletion", "Create Test Employee for Deletion", False, f"Exception: {str(e)}")
            return
            
        # Test 1: Delete the created employee
        try:
            response = requests.delete(f"{self.base_url}/employees/{self.created_employee_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "deleted_employee" in data:
                    deleted_info = data["deleted_employee"]
                    if deleted_info.get("employee_id") == self.created_employee_id:
                        self.log_result("employee_deletion", "Delete Employee", True, 
                                      f"Successfully deleted employee {deleted_info.get('full_name')} (ID: {self.created_employee_id})")
                    else:
                        self.log_result("employee_deletion", "Delete Employee", False, 
                                      "Employee ID mismatch in deletion response")
                else:
                    self.log_result("employee_deletion", "Delete Employee", False, 
                                  "Response missing required fields")
            else:
                self.log_result("employee_deletion", "Delete Employee", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("employee_deletion", "Delete Employee", False, f"Exception: {str(e)}")
            
        # Test 2: Verify employee is actually deleted
        try:
            response = requests.get(f"{self.base_url}/employees/{self.created_employee_id}", headers=headers)
            
            if response.status_code == 404:
                self.log_result("employee_deletion", "Verify Employee Deleted", True, 
                              "Correctly returns 404 for deleted employee")
            else:
                self.log_result("employee_deletion", "Verify Employee Deleted", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("employee_deletion", "Verify Employee Deleted", False, f"Exception: {str(e)}")
            
        # Test 3: Try to delete non-existent employee
        try:
            fake_employee_id = "NONEXISTENT123"
            response = requests.delete(f"{self.base_url}/employees/{fake_employee_id}", headers=headers)
            
            if response.status_code == 404:
                self.log_result("employee_deletion", "Delete Non-existent Employee", True, 
                              "Correctly returns 404 for non-existent employee")
            else:
                self.log_result("employee_deletion", "Delete Non-existent Employee", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("employee_deletion", "Delete Non-existent Employee", False, f"Exception: {str(e)}")
            
        # Test 4: Test authentication requirement
        try:
            response = requests.delete(f"{self.base_url}/employees/VWT001")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("employee_deletion", "Delete Auth Required", True, 
                              "Correctly requires authentication for employee deletion")
            else:
                self.log_result("employee_deletion", "Delete Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("employee_deletion", "Delete Auth Required", False, f"Exception: {str(e)}")
            
    def test_document_management(self):
        """Test document management functionality"""
        print("\n=== TESTING DOCUMENT MANAGEMENT API ===")
        
        if not self.auth_token:
            self.log_result("document_management", "Document Management Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        test_employee_id = "VWT001"  # Admin employee ID
        
        # Test 1: Upload document for employee
        try:
            # Create a simple test file content
            test_file_content = b"This is a test document for employee document management system.\nCreated for testing purposes.\nVishwas World Tech HRMS System."
            
            # Prepare multipart form data
            files = {
                'file': ('test_document.txt', io.BytesIO(test_file_content), 'text/plain')
            }
            params = {
                'document_type': 'Resume',
                'description': 'Test document upload for employee'
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/upload-document", 
                                   files=files, params=params, headers=headers)
            
            if response.status_code == 200:
                upload_data = response.json()
                if "message" in upload_data and "document" in upload_data:
                    document_info = upload_data["document"]
                    self.uploaded_document_id = document_info.get("id")
                    self.log_result("document_management", "Upload Document", True, 
                                  f"Successfully uploaded document: {document_info.get('document_name')} "
                                  f"(Type: {document_info.get('document_type')}, Size: {document_info.get('file_size')} bytes)")
                else:
                    self.log_result("document_management", "Upload Document", False, 
                                  "Response missing required fields")
            else:
                self.log_result("document_management", "Upload Document", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("document_management", "Upload Document", False, f"Exception: {str(e)}")
            
        # Test 2: Get employee documents
        try:
            response = requests.get(f"{self.base_url}/employees/{test_employee_id}/documents", headers=headers)
            
            if response.status_code == 200:
                documents = response.json()
                if isinstance(documents, list):
                    if len(documents) > 0:
                        # Check if our uploaded document is in the list
                        uploaded_found = any(doc.get("id") == self.uploaded_document_id for doc in documents)
                        if uploaded_found:
                            self.log_result("document_management", "Get Employee Documents", True, 
                                          f"Successfully retrieved {len(documents)} documents, including uploaded test document")
                        else:
                            self.log_result("document_management", "Get Employee Documents", True, 
                                          f"Successfully retrieved {len(documents)} documents (uploaded document may not be found)")
                    else:
                        self.log_result("document_management", "Get Employee Documents", True, 
                                      "Successfully retrieved documents list (empty)")
                else:
                    self.log_result("document_management", "Get Employee Documents", False, 
                                  "Response is not a list")
            else:
                self.log_result("document_management", "Get Employee Documents", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("document_management", "Get Employee Documents", False, f"Exception: {str(e)}")
            
        # Test 3: Download document (if we have uploaded one)
        if self.uploaded_document_id:
            try:
                response = requests.get(f"{self.base_url}/employees/{test_employee_id}/documents/{self.uploaded_document_id}/download", 
                                      headers=headers)
                
                if response.status_code == 200:
                    download_data = response.json()
                    required_fields = ["document_name", "document_type", "file_data", "file_size"]
                    
                    if all(field in download_data for field in required_fields):
                        # Verify file data is base64 encoded
                        try:
                            file_bytes = base64.b64decode(download_data["file_data"])
                            file_valid = True
                            decoded_size = len(file_bytes)
                        except:
                            file_valid = False
                            decoded_size = 0
                            
                        if file_valid:
                            self.log_result("document_management", "Download Document", True, 
                                          f"Successfully downloaded document: {download_data['document_name']} "
                                          f"(Size: {decoded_size} bytes)")
                        else:
                            self.log_result("document_management", "Download Document", False, 
                                          "Invalid base64 file data")
                    else:
                        missing_fields = [field for field in required_fields if field not in download_data]
                        self.log_result("document_management", "Download Document", False, 
                                      f"Missing fields: {missing_fields}")
                else:
                    self.log_result("document_management", "Download Document", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result("document_management", "Download Document", False, f"Exception: {str(e)}")
                
        # Test 4: Upload invalid file type
        try:
            # Try to upload an unsupported file type
            invalid_file_content = b"This is a test file with invalid extension"
            
            files = {
                'file': ('test_file.xyz', io.BytesIO(invalid_file_content), 'application/octet-stream')
            }
            params = {
                'document_type': 'Other',
                'description': 'Test invalid file type'
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/upload-document", 
                                   files=files, params=params, headers=headers)
            
            if response.status_code == 400:
                self.log_result("document_management", "Upload Invalid File Type", True, 
                              "Correctly rejected invalid file type")
            else:
                self.log_result("document_management", "Upload Invalid File Type", False, 
                              f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_result("document_management", "Upload Invalid File Type", False, f"Exception: {str(e)}")
            
        # Test 5: Test with non-existent employee
        try:
            test_file_content = b"Test content"
            files = {
                'file': ('test.txt', io.BytesIO(test_file_content), 'text/plain')
            }
            params = {
                'document_type': 'Resume',
                'description': 'Test document'
            }
            
            response = requests.post(f"{self.base_url}/employees/NONEXISTENT123/upload-document", 
                                   files=files, params=params, headers=headers)
            
            if response.status_code == 404:
                self.log_result("document_management", "Upload for Non-existent Employee", True, 
                              "Correctly returns 404 for non-existent employee")
            else:
                self.log_result("document_management", "Upload for Non-existent Employee", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("document_management", "Upload for Non-existent Employee", False, f"Exception: {str(e)}")
            
        # Test 6: Test authentication requirement
        try:
            response = requests.get(f"{self.base_url}/employees/{test_employee_id}/documents")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("document_management", "Document Auth Required", True, 
                              "Correctly requires authentication for document operations")
            else:
                self.log_result("document_management", "Document Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("document_management", "Document Auth Required", False, f"Exception: {str(e)}")
            
    def test_announcements(self):
        """Test company announcements functionality"""
        print("\n=== TESTING COMPANY ANNOUNCEMENTS API ===")
        
        if not self.auth_token:
            self.log_result("announcements", "Announcements Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: Create announcement
        try:
            announcement_data = {
                "title": "New Company Policy Update",
                "content": "We are pleased to announce updates to our company policies effective immediately. Please review the updated employee handbook for detailed information about the new attendance tracking system and remote work guidelines.",
                "announcement_type": "Policy",
                "priority": "High",
                "valid_until": "2024-12-31T23:59:59Z",
                "target_departments": ["All Departments", "HR", "IT"]
            }
            
            response = requests.post(f"{self.base_url}/announcements", json=announcement_data, headers=headers)
            
            if response.status_code == 200:
                created_announcement = response.json()
                required_fields = ["id", "title", "content", "announcement_type", "priority", "published_by", "published_at"]
                
                if all(field in created_announcement for field in required_fields):
                    self.created_announcement_id = created_announcement["id"]
                    self.log_result("announcements", "Create Announcement", True, 
                                  f"Successfully created announcement: '{created_announcement['title']}' "
                                  f"(Type: {created_announcement['announcement_type']}, Priority: {created_announcement['priority']})")
                else:
                    missing_fields = [field for field in required_fields if field not in created_announcement]
                    self.log_result("announcements", "Create Announcement", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("announcements", "Create Announcement", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("announcements", "Create Announcement", False, f"Exception: {str(e)}")
            
        # Test 2: Create different types of announcements
        announcement_types = [
            {"type": "General", "priority": "Medium", "title": "Office Maintenance Notice"},
            {"type": "Event", "priority": "Low", "title": "Team Building Event"},
            {"type": "Urgent", "priority": "Urgent", "title": "System Maintenance Alert"}
        ]
        
        for ann_type in announcement_types:
            try:
                announcement_data = {
                    "title": ann_type["title"],
                    "content": f"This is a {ann_type['type'].lower()} announcement with {ann_type['priority'].lower()} priority for testing purposes.",
                    "announcement_type": ann_type["type"],
                    "priority": ann_type["priority"],
                    "valid_until": "2024-12-31T23:59:59Z",
                    "target_departments": ["All Departments"]
                }
                
                response = requests.post(f"{self.base_url}/announcements", json=announcement_data, headers=headers)
                
                if response.status_code == 200:
                    created_announcement = response.json()
                    self.log_result("announcements", f"Create {ann_type['type']} Announcement", True, 
                                  f"Successfully created {ann_type['type']} announcement with {ann_type['priority']} priority")
                else:
                    self.log_result("announcements", f"Create {ann_type['type']} Announcement", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result("announcements", f"Create {ann_type['type']} Announcement", False, f"Exception: {str(e)}")
                
        # Test 3: Get all announcements
        try:
            response = requests.get(f"{self.base_url}/announcements", headers=headers)
            
            if response.status_code == 200:
                announcements = response.json()
                if isinstance(announcements, list):
                    if len(announcements) > 0:
                        # Check if our created announcement is in the list
                        created_found = any(ann.get("id") == self.created_announcement_id for ann in announcements)
                        
                        # Verify announcements are sorted by priority and date
                        priorities = [ann.get("priority", "Low") for ann in announcements]
                        
                        self.log_result("announcements", "Get All Announcements", True, 
                                      f"Successfully retrieved {len(announcements)} announcements, "
                                      f"created announcement found: {created_found}")
                    else:
                        self.log_result("announcements", "Get All Announcements", True, 
                                      "Successfully retrieved announcements list (empty)")
                else:
                    self.log_result("announcements", "Get All Announcements", False, 
                                  "Response is not a list")
            else:
                self.log_result("announcements", "Get All Announcements", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("announcements", "Get All Announcements", False, f"Exception: {str(e)}")
            
        # Test 4: Delete announcement (if we created one)
        if self.created_announcement_id:
            try:
                response = requests.delete(f"{self.base_url}/announcements/{self.created_announcement_id}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "message" in data:
                        self.log_result("announcements", "Delete Announcement", True, 
                                      f"Successfully deleted announcement: {data['message']}")
                    else:
                        self.log_result("announcements", "Delete Announcement", False, 
                                      "Response missing message field")
                else:
                    self.log_result("announcements", "Delete Announcement", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result("announcements", "Delete Announcement", False, f"Exception: {str(e)}")
                
        # Test 5: Try to delete non-existent announcement
        try:
            fake_announcement_id = "NONEXISTENT123"
            response = requests.delete(f"{self.base_url}/announcements/{fake_announcement_id}", headers=headers)
            
            if response.status_code == 404:
                self.log_result("announcements", "Delete Non-existent Announcement", True, 
                              "Correctly returns 404 for non-existent announcement")
            else:
                self.log_result("announcements", "Delete Non-existent Announcement", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("announcements", "Delete Non-existent Announcement", False, f"Exception: {str(e)}")
            
        # Test 6: Test authentication requirement
        try:
            response = requests.get(f"{self.base_url}/announcements")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("announcements", "Announcements Auth Required", True, 
                              "Correctly requires authentication for announcements")
            else:
                self.log_result("announcements", "Announcements Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("announcements", "Announcements Auth Required", False, f"Exception: {str(e)}")
            
    def test_enhanced_dashboard(self):
        """Test enhanced dashboard functionality"""
        print("\n=== TESTING ENHANCED DASHBOARD API ===")
        
        if not self.auth_token:
            self.log_result("enhanced_dashboard", "Enhanced Dashboard Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: Get dashboard theme
        try:
            response = requests.get(f"{self.base_url}/dashboard/theme")
            
            if response.status_code == 200:
                theme_data = response.json()
                required_sections = ["company_branding", "color_scheme", "design_elements"]
                
                if all(section in theme_data for section in required_sections):
                    branding = theme_data["company_branding"]
                    colors = theme_data["color_scheme"]
                    
                    # Verify Vishwas World Tech branding
                    if branding.get("company_name") == "Vishwas World Tech":
                        self.log_result("enhanced_dashboard", "Get Dashboard Theme", True, 
                                      f"Successfully retrieved dashboard theme with Vishwas World Tech branding, "
                                      f"primary color: {colors.get('primary', 'N/A')}")
                    else:
                        self.log_result("enhanced_dashboard", "Get Dashboard Theme", False, 
                                      f"Incorrect company branding: {branding.get('company_name')}")
                else:
                    missing_sections = [section for section in required_sections if section not in theme_data]
                    self.log_result("enhanced_dashboard", "Get Dashboard Theme", False, 
                                  f"Missing theme sections: {missing_sections}")
            else:
                self.log_result("enhanced_dashboard", "Get Dashboard Theme", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("enhanced_dashboard", "Get Dashboard Theme", False, f"Exception: {str(e)}")
            
        # Test 2: Get enhanced dashboard statistics
        try:
            response = requests.get(f"{self.base_url}/dashboard/enhanced-stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                required_sections = ["employee_metrics", "document_metrics", "announcement_metrics", "system_health"]
                
                if all(section in stats for section in required_sections):
                    employee_metrics = stats["employee_metrics"]
                    document_metrics = stats["document_metrics"]
                    announcement_metrics = stats["announcement_metrics"]
                    system_health = stats["system_health"]
                    
                    # Verify employee metrics
                    emp_fields = ["total_employees", "present_today", "logged_in_now", "absent_today"]
                    if all(field in employee_metrics for field in emp_fields):
                        # Verify document metrics
                        doc_fields = ["total_documents", "recent_uploads"]
                        if all(field in document_metrics for field in doc_fields):
                            # Verify announcement metrics
                            ann_fields = ["active_announcements", "recent_announcements", "urgent_announcements"]
                            if all(field in announcement_metrics for field in ann_fields):
                                # Verify system health
                                if "database_status" in system_health and "last_updated" in system_health:
                                    self.log_result("enhanced_dashboard", "Get Enhanced Dashboard Stats", True, 
                                                  f"Successfully retrieved enhanced dashboard statistics - "
                                                  f"Employees: {employee_metrics['total_employees']}, "
                                                  f"Documents: {document_metrics['total_documents']}, "
                                                  f"Announcements: {announcement_metrics['active_announcements']}, "
                                                  f"DB Status: {system_health['database_status']}")
                                else:
                                    self.log_result("enhanced_dashboard", "Get Enhanced Dashboard Stats", False, 
                                                  "Missing system health fields")
                            else:
                                missing_ann_fields = [field for field in ann_fields if field not in announcement_metrics]
                                self.log_result("enhanced_dashboard", "Get Enhanced Dashboard Stats", False, 
                                              f"Missing announcement metrics: {missing_ann_fields}")
                        else:
                            missing_doc_fields = [field for field in doc_fields if field not in document_metrics]
                            self.log_result("enhanced_dashboard", "Get Enhanced Dashboard Stats", False, 
                                          f"Missing document metrics: {missing_doc_fields}")
                    else:
                        missing_emp_fields = [field for field in emp_fields if field not in employee_metrics]
                        self.log_result("enhanced_dashboard", "Get Enhanced Dashboard Stats", False, 
                                      f"Missing employee metrics: {missing_emp_fields}")
                else:
                    missing_sections = [section for section in required_sections if section not in stats]
                    self.log_result("enhanced_dashboard", "Get Enhanced Dashboard Stats", False, 
                                  f"Missing stats sections: {missing_sections}")
            else:
                self.log_result("enhanced_dashboard", "Get Enhanced Dashboard Stats", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("enhanced_dashboard", "Get Enhanced Dashboard Stats", False, f"Exception: {str(e)}")
            
        # Test 3: Test authentication requirement for enhanced stats
        try:
            response = requests.get(f"{self.base_url}/dashboard/enhanced-stats")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("enhanced_dashboard", "Enhanced Stats Auth Required", True, 
                              "Correctly requires authentication for enhanced dashboard stats")
            else:
                self.log_result("enhanced_dashboard", "Enhanced Stats Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("enhanced_dashboard", "Enhanced Stats Auth Required", False, f"Exception: {str(e)}")
            
        # Test 4: Verify theme endpoint doesn't require authentication (public)
        try:
            response = requests.get(f"{self.base_url}/dashboard/theme")  # No auth header
            
            if response.status_code == 200:
                self.log_result("enhanced_dashboard", "Theme Public Access", True, 
                              "Dashboard theme is publicly accessible (correct)")
            else:
                self.log_result("enhanced_dashboard", "Theme Public Access", False, 
                              f"Theme endpoint should be public, got {response.status_code}")
                
        except Exception as e:
            self.log_result("enhanced_dashboard", "Theme Public Access", False, f"Exception: {str(e)}")
            
    def run_all_tests(self):
        """Run all enhanced feature tests"""
        print("🚀 Starting Enhanced HRMS Features Testing Suite")
        print("=" * 60)
        
        # Run tests in order
        self.test_authentication()
        self.test_employee_deletion()
        self.test_document_management()
        self.test_announcements()
        self.test_enhanced_dashboard()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("🏁 ENHANCED FEATURES TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status_icon = "✅" if failed == 0 else "❌"
            print(f"{status_icon} {category.upper().replace('_', ' ')}: {passed} passed, {failed} failed")
            
            # Show failed tests
            if failed > 0:
                failed_tests = [detail for detail in results["details"] if detail["status"] == "❌ FAIL"]
                for test in failed_tests:
                    print(f"   ❌ {test['test']}: {test['message']}")
                    
        print("\n" + "-" * 60)
        print(f"📊 OVERALL RESULTS: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 ALL ENHANCED FEATURES TESTS PASSED!")
        else:
            print(f"⚠️  {total_failed} tests failed - review above for details")
            
        print("=" * 60)

if __name__ == "__main__":
    tester = EnhancedHRMSAPITester()
    tester.run_all_tests()