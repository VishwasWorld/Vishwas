#!/usr/bin/env python3
"""
Multi-Channel Communication Features Testing Suite
Tests the NEW multi-channel communication endpoints for HRMS system
"""

import requests
import json
from datetime import datetime, timezone
import time

# Configuration
BASE_URL = "https://vishwashrms.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class MultiChannelCommunicationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_results = {
            "multi_channel_salary": {"passed": 0, "failed": 0, "details": []},
            "announcement_sharing": {"passed": 0, "failed": 0, "details": []},
            "hr_notifications": {"passed": 0, "failed": 0, "details": []},
            "communication_config": {"passed": 0, "failed": 0, "details": []},
            "digital_signature": {"passed": 0, "failed": 0, "details": []}
        }
        self.created_announcement_id = None
        
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
        print("\n=== AUTHENTICATING FOR MULTI-CHANNEL COMMUNICATION TESTS ===")
        
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
        
    def test_enhanced_multi_channel_salary_slip_sharing(self):
        """Test enhanced multi-channel salary slip sharing endpoint"""
        print("\n=== TESTING ENHANCED MULTI-CHANNEL SALARY SLIP SHARING ===")
        
        if not self.auth_token:
            self.log_result("multi_channel_salary", "Multi-channel Salary Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        test_employee_id = "00001"  # Using existing employee from system
        
        # Test 1: Multi-channel salary slip sharing with all channels
        try:
            request_data = {
                "month": 1,
                "year": 2025,
                "channels": ["email", "whatsapp", "sms"]
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/share-salary-slip", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["message", "employee_id", "employee_name", "month", "year", "channels_attempted", "sharing_results"]
                
                if all(field in data for field in required_fields):
                    sharing_results = data.get("sharing_results", {})
                    channels_attempted = data.get("channels_attempted", [])
                    
                    # Verify all channels were attempted
                    if set(channels_attempted) == {"email", "whatsapp", "sms"}:
                        # Check sharing results for each channel
                        channel_status = []
                        for channel in ["email", "whatsapp", "sms"]:
                            if channel in sharing_results:
                                result = sharing_results[channel]
                                status = result.get("status", "unknown")
                                channel_status.append(f"{channel}: {status}")
                            else:
                                channel_status.append(f"{channel}: missing")
                        
                        self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - All Channels", True, 
                                      f"Successfully attempted sharing via all channels for {data['employee_name']} (Jan 2025). "
                                      f"Channel results: {'; '.join(channel_status)}")
                    else:
                        self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - All Channels", False, 
                                      f"Expected channels [email, whatsapp, sms], got {channels_attempted}")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - All Channels", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - All Channels", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - All Channels", False, f"Exception: {str(e)}")
            
        # Test 2: Multi-channel salary slip sharing with email and WhatsApp only
        try:
            request_data = {
                "month": 1,
                "year": 2025,
                "channels": ["email", "whatsapp"]
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/share-salary-slip", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                sharing_results = data.get("sharing_results", {})
                channels_attempted = data.get("channels_attempted", [])
                
                if set(channels_attempted) == {"email", "whatsapp"}:
                    # Verify only email and whatsapp results are present
                    if "email" in sharing_results and "whatsapp" in sharing_results and "sms" not in sharing_results:
                        self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Email & WhatsApp", True, 
                                      f"Successfully shared via email and WhatsApp only for {data['employee_name']} (Jan 2025)")
                    else:
                        self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Email & WhatsApp", False, 
                                      f"Unexpected sharing results: {list(sharing_results.keys())}")
                else:
                    self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Email & WhatsApp", False, 
                                  f"Expected channels [email, whatsapp], got {channels_attempted}")
            else:
                self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Email & WhatsApp", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Email & WhatsApp", False, f"Exception: {str(e)}")
            
        # Test 3: Multi-channel salary slip sharing with single email channel
        try:
            request_data = {
                "month": 1,
                "year": 2025,
                "channels": ["email"]
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/share-salary-slip", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                sharing_results = data.get("sharing_results", {})
                channels_attempted = data.get("channels_attempted", [])
                
                if channels_attempted == ["email"]:
                    if "email" in sharing_results and len(sharing_results) == 1:
                        email_result = sharing_results["email"]
                        self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Email Only", True, 
                                      f"Successfully shared via email only for {data['employee_name']} (Jan 2025). "
                                      f"Email status: {email_result.get('status', 'unknown')}")
                    else:
                        self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Email Only", False, 
                                      f"Expected only email result, got: {list(sharing_results.keys())}")
                else:
                    self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Email Only", False, 
                                  f"Expected channels [email], got {channels_attempted}")
            else:
                self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Email Only", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Email Only", False, f"Exception: {str(e)}")
            
        # Test 4: Test with invalid employee ID
        try:
            request_data = {
                "month": 1,
                "year": 2025,
                "channels": ["email"]
            }
            
            response = requests.post(f"{self.base_url}/employees/INVALID123/share-salary-slip", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 404:
                self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Invalid Employee", True, 
                              "Correctly returned 404 for invalid employee ID")
            else:
                self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Invalid Employee", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Invalid Employee", False, f"Exception: {str(e)}")
            
        # Test 5: Test authentication requirement
        try:
            request_data = {
                "month": 1,
                "year": 2025,
                "channels": ["email"]
            }
            
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/share-salary-slip", 
                                   json=request_data)  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Auth Required", True, 
                              "Correctly requires authentication")
            else:
                self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("multi_channel_salary", "Multi-channel Salary Slip Sharing - Auth Required", False, f"Exception: {str(e)}")
            
    def test_digital_salary_slip_with_signature(self):
        """Test digital salary slip generation with signature"""
        print("\n=== TESTING DIGITAL SALARY SLIP WITH SIGNATURE ===")
        
        if not self.auth_token:
            self.log_result("digital_signature", "Digital Signature Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        test_employee_id = "00001"  # Using existing employee from system
        
        # Test 1: Generate digital salary slip with signature
        try:
            response = requests.post(f"{self.base_url}/employees/{test_employee_id}/generate-digital-salary-slip", 
                                   params={"month": 1, "year": 2025}, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["message", "employee_id", "employee_name", "month", "year", "pdf_data", "filename", "digital_signature"]
                
                if all(field in data for field in required_fields):
                    digital_signature = data.get("digital_signature", {})
                    
                    # Verify digital signature contains required information
                    signature_fields = ["signature_id", "generated_at", "verification_url"]
                    if all(field in digital_signature for field in signature_fields):
                        # Verify PDF data is substantial (should include signature)
                        pdf_size = len(data.get("pdf_data", ""))
                        if pdf_size > 50000:  # Should be substantial with signature
                            self.log_result("digital_signature", "Generate Digital Salary Slip with Signature", True, 
                                          f"Successfully generated digital salary slip for {data['employee_name']} (Jan 2025) "
                                          f"with signature ID: {digital_signature['signature_id']}, PDF size: {pdf_size} chars")
                        else:
                            self.log_result("digital_signature", "Generate Digital Salary Slip with Signature", False, 
                                          f"PDF size too small for digital signature: {pdf_size} chars")
                    else:
                        missing_sig_fields = [field for field in signature_fields if field not in digital_signature]
                        self.log_result("digital_signature", "Generate Digital Salary Slip with Signature", False, 
                                      f"Missing digital signature fields: {missing_sig_fields}")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("digital_signature", "Generate Digital Salary Slip with Signature", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("digital_signature", "Generate Digital Salary Slip with Signature", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("digital_signature", "Generate Digital Salary Slip with Signature", False, f"Exception: {str(e)}")
            
        # Test 2: Test with invalid employee ID
        try:
            response = requests.post(f"{self.base_url}/employees/INVALID123/generate-digital-salary-slip", 
                                   params={"month": 1, "year": 2025}, headers=headers)
            
            if response.status_code == 404:
                self.log_result("digital_signature", "Digital Salary Slip - Invalid Employee", True, 
                              "Correctly returned 404 for invalid employee ID")
            else:
                self.log_result("digital_signature", "Digital Salary Slip - Invalid Employee", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("digital_signature", "Digital Salary Slip - Invalid Employee", False, f"Exception: {str(e)}")
            
    def create_test_announcement(self):
        """Create a test announcement for sharing tests"""
        if not self.auth_token:
            return None
            
        headers = self.get_auth_headers()
        
        try:
            announcement_data = {
                "title": "Test Company Announcement for Multi-channel Sharing",
                "content": "This is a test announcement to verify multi-channel sharing functionality. Please ignore this message.",
                "announcement_type": "General",
                "priority": "Medium",
                "valid_until": "2025-12-31T23:59:59Z",
                "target_departments": ["All"]
            }
            
            response = requests.post(f"{self.base_url}/announcements", 
                                   json=announcement_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.created_announcement_id = data.get("id")
                print(f"✅ Created test announcement with ID: {self.created_announcement_id}")
                return self.created_announcement_id
            else:
                print(f"❌ Failed to create test announcement: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception creating test announcement: {str(e)}")
            return None
            
    def test_company_announcement_multi_channel_sharing(self):
        """Test company announcement multi-channel sharing"""
        print("\n=== TESTING COMPANY ANNOUNCEMENT MULTI-CHANNEL SHARING ===")
        
        if not self.auth_token:
            self.log_result("announcement_sharing", "Announcement Sharing Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Create test announcement first
        announcement_id = self.create_test_announcement()
        if not announcement_id:
            self.log_result("announcement_sharing", "Create Test Announcement", False, "Failed to create test announcement")
            return
            
        # Test 1: Share announcement via email and WhatsApp
        try:
            request_data = {
                "announcement_id": announcement_id,
                "channels": ["email", "whatsapp"]
            }
            
            response = requests.post(f"{self.base_url}/announcements/{announcement_id}/share", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["message", "announcement_id", "announcement_title", "target_employees", "channels_attempted", "sharing_results"]
                
                if all(field in data for field in required_fields):
                    sharing_results = data.get("sharing_results", {})
                    channels_attempted = data.get("channels_attempted", [])
                    target_employees = data.get("target_employees", 0)
                    
                    if set(channels_attempted) == {"email", "whatsapp"}:
                        # Check sharing results for each channel
                        channel_status = []
                        for channel in ["email", "whatsapp"]:
                            if channel in sharing_results:
                                result = sharing_results[channel]
                                status = result.get("status", "unknown")
                                total_sent = result.get("total_sent", 0)
                                channel_status.append(f"{channel}: {status} ({total_sent} sent)")
                            else:
                                channel_status.append(f"{channel}: missing")
                        
                        self.log_result("announcement_sharing", "Company Announcement Sharing - Email & WhatsApp", True, 
                                      f"Successfully shared announcement '{data['announcement_title']}' to {target_employees} employees. "
                                      f"Channel results: {'; '.join(channel_status)}")
                    else:
                        self.log_result("announcement_sharing", "Company Announcement Sharing - Email & WhatsApp", False, 
                                      f"Expected channels [email, whatsapp], got {channels_attempted}")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("announcement_sharing", "Company Announcement Sharing - Email & WhatsApp", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("announcement_sharing", "Company Announcement Sharing - Email & WhatsApp", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("announcement_sharing", "Company Announcement Sharing - Email & WhatsApp", False, f"Exception: {str(e)}")
            
        # Test 2: Share announcement via email only
        try:
            request_data = {
                "announcement_id": announcement_id,
                "channels": ["email"]
            }
            
            response = requests.post(f"{self.base_url}/announcements/{announcement_id}/share", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                sharing_results = data.get("sharing_results", {})
                channels_attempted = data.get("channels_attempted", [])
                
                if channels_attempted == ["email"]:
                    if "email" in sharing_results and len(sharing_results) == 1:
                        email_result = sharing_results["email"]
                        self.log_result("announcement_sharing", "Company Announcement Sharing - Email Only", True, 
                                      f"Successfully shared announcement via email only. "
                                      f"Email status: {email_result.get('status', 'unknown')}")
                    else:
                        self.log_result("announcement_sharing", "Company Announcement Sharing - Email Only", False, 
                                      f"Expected only email result, got: {list(sharing_results.keys())}")
                else:
                    self.log_result("announcement_sharing", "Company Announcement Sharing - Email Only", False, 
                                  f"Expected channels [email], got {channels_attempted}")
            else:
                self.log_result("announcement_sharing", "Company Announcement Sharing - Email Only", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("announcement_sharing", "Company Announcement Sharing - Email Only", False, f"Exception: {str(e)}")
            
        # Test 3: Test with invalid announcement ID
        try:
            request_data = {
                "announcement_id": "INVALID123",
                "channels": ["email"]
            }
            
            response = requests.post(f"{self.base_url}/announcements/INVALID123/share", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 404:
                self.log_result("announcement_sharing", "Company Announcement Sharing - Invalid Announcement", True, 
                              "Correctly returned 404 for invalid announcement ID")
            else:
                self.log_result("announcement_sharing", "Company Announcement Sharing - Invalid Announcement", False, 
                              f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("announcement_sharing", "Company Announcement Sharing - Invalid Announcement", False, f"Exception: {str(e)}")
            
    def test_hr_notification_system(self):
        """Test HR notification system"""
        print("\n=== TESTING HR NOTIFICATION SYSTEM ===")
        
        if not self.auth_token:
            self.log_result("hr_notifications", "HR Notification Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: Send HR notification via all channels
        try:
            request_data = {
                "title": "Test HR Notification",
                "message": "This is a test HR notification to verify multi-channel communication functionality.",
                "channels": ["email", "whatsapp", "sms"],
                "priority": "normal"
            }
            
            response = requests.post(f"{self.base_url}/notifications/send", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["message", "notification_title", "channels_attempted", "sharing_results", "target_employees"]
                
                if all(field in data for field in required_fields):
                    sharing_results = data.get("sharing_results", {})
                    channels_attempted = data.get("channels_attempted", [])
                    target_employees = data.get("target_employees", 0)
                    
                    if set(channels_attempted) == {"email", "whatsapp", "sms"}:
                        # Check sharing results for each channel
                        channel_status = []
                        for channel in ["email", "whatsapp", "sms"]:
                            if channel in sharing_results:
                                result = sharing_results[channel]
                                status = result.get("status", "unknown")
                                total_sent = result.get("total_sent", 0)
                                channel_status.append(f"{channel}: {status} ({total_sent} sent)")
                            else:
                                channel_status.append(f"{channel}: missing")
                        
                        self.log_result("hr_notifications", "HR Notification - All Channels", True, 
                                      f"Successfully sent HR notification '{data['notification_title']}' to {target_employees} employees. "
                                      f"Channel results: {'; '.join(channel_status)}")
                    else:
                        self.log_result("hr_notifications", "HR Notification - All Channels", False, 
                                      f"Expected channels [email, whatsapp, sms], got {channels_attempted}")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("hr_notifications", "HR Notification - All Channels", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("hr_notifications", "HR Notification - All Channels", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("hr_notifications", "HR Notification - All Channels", False, f"Exception: {str(e)}")
            
        # Test 2: Send HR notification with high priority
        try:
            request_data = {
                "title": "Urgent HR Notification",
                "message": "This is an urgent HR notification test.",
                "channels": ["email", "whatsapp"],
                "priority": "high"
            }
            
            response = requests.post(f"{self.base_url}/notifications/send", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                sharing_results = data.get("sharing_results", {})
                channels_attempted = data.get("channels_attempted", [])
                
                if set(channels_attempted) == {"email", "whatsapp"}:
                    self.log_result("hr_notifications", "HR Notification - High Priority", True, 
                                  f"Successfully sent high priority HR notification via email and WhatsApp")
                else:
                    self.log_result("hr_notifications", "HR Notification - High Priority", False, 
                                  f"Expected channels [email, whatsapp], got {channels_attempted}")
            else:
                self.log_result("hr_notifications", "HR Notification - High Priority", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("hr_notifications", "HR Notification - High Priority", False, f"Exception: {str(e)}")
            
        # Test 3: Test authentication requirement
        try:
            request_data = {
                "title": "Test Notification",
                "message": "Test message",
                "channels": ["email"]
            }
            
            response = requests.post(f"{self.base_url}/notifications/send", 
                                   json=request_data)  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("hr_notifications", "HR Notification - Auth Required", True, 
                              "Correctly requires authentication")
            else:
                self.log_result("hr_notifications", "HR Notification - Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("hr_notifications", "HR Notification - Auth Required", False, f"Exception: {str(e)}")
            
    def test_communication_configuration(self):
        """Test communication configuration endpoint"""
        print("\n=== TESTING COMMUNICATION CONFIGURATION ===")
        
        if not self.auth_token:
            self.log_result("communication_config", "Communication Config Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: Get communication configuration
        try:
            response = requests.get(f"{self.base_url}/communication/config", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["email", "whatsapp", "sms"]
                
                if all(field in data for field in required_fields):
                    # Check service configurations
                    email_config = data.get("email", {})
                    whatsapp_config = data.get("whatsapp", {})
                    sms_config = data.get("sms", {})
                    
                    config_status = []
                    for service, config in [("email", email_config), ("whatsapp", whatsapp_config), ("sms", sms_config)]:
                        service_name = config.get("service", "unknown")
                        configured = config.get("configured", False)
                        config_status.append(f"{service}: {service_name} ({'configured' if configured else 'not configured'})")
                    
                    self.log_result("communication_config", "Get Communication Configuration", True, 
                                  f"Successfully retrieved communication configuration. "
                                  f"Service status: {'; '.join(config_status)}")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("communication_config", "Get Communication Configuration", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("communication_config", "Get Communication Configuration", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("communication_config", "Get Communication Configuration", False, f"Exception: {str(e)}")
            
        # Test 2: Test authentication requirement
        try:
            response = requests.get(f"{self.base_url}/communication/config")  # No auth header
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("communication_config", "Communication Config - Auth Required", True, 
                              "Correctly requires authentication")
            else:
                self.log_result("communication_config", "Communication Config - Auth Required", False, 
                              f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("communication_config", "Communication Config - Auth Required", False, f"Exception: {str(e)}")
            
    def test_communication_testing(self):
        """Test communication testing endpoint"""
        print("\n=== TESTING COMMUNICATION TESTING ENDPOINT ===")
        
        if not self.auth_token:
            self.log_result("communication_config", "Communication Testing Tests", False, "No auth token available")
            return
            
        headers = self.get_auth_headers()
        
        # Test 1: Test communication services with sample data
        try:
            request_data = {
                "test_email": "test@vishwasworld.com",
                "test_phone": "+91-9876543210",
                "channels": ["email", "whatsapp", "sms"]
            }
            
            response = requests.post(f"{self.base_url}/communication/test", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["message", "test_results"]
                
                if all(field in data for field in required_fields):
                    test_results = data.get("test_results", {})
                    
                    # Check test results for each channel
                    channel_test_status = []
                    for channel in ["email", "whatsapp", "sms"]:
                        if channel in test_results:
                            result = test_results[channel]
                            status = result.get("status", "unknown")
                            channel_test_status.append(f"{channel}: {status}")
                        else:
                            channel_test_status.append(f"{channel}: missing")
                    
                    self.log_result("communication_config", "Communication Service Testing", True, 
                                  f"Successfully tested communication services. "
                                  f"Test results: {'; '.join(channel_test_status)}")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_result("communication_config", "Communication Service Testing", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("communication_config", "Communication Service Testing", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("communication_config", "Communication Service Testing", False, f"Exception: {str(e)}")
            
        # Test 2: Test with specific channels only
        try:
            request_data = {
                "test_email": "test@vishwasworld.com",
                "channels": ["email"]
            }
            
            response = requests.post(f"{self.base_url}/communication/test", 
                                   json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                test_results = data.get("test_results", {})
                
                if "email" in test_results and len(test_results) == 1:
                    email_result = test_results["email"]
                    self.log_result("communication_config", "Communication Testing - Email Only", True, 
                                  f"Successfully tested email service only. Status: {email_result.get('status', 'unknown')}")
                else:
                    self.log_result("communication_config", "Communication Testing - Email Only", False, 
                                  f"Expected only email test result, got: {list(test_results.keys())}")
            else:
                self.log_result("communication_config", "Communication Testing - Email Only", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("communication_config", "Communication Testing - Email Only", False, f"Exception: {str(e)}")
            
    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n=== CLEANING UP TEST DATA ===")
        
        if not self.auth_token:
            return
            
        headers = self.get_auth_headers()
        
        # Delete test announcement if created
        if self.created_announcement_id:
            try:
                response = requests.delete(f"{self.base_url}/announcements/{self.created_announcement_id}", 
                                         headers=headers)
                if response.status_code == 200:
                    print(f"✅ Deleted test announcement: {self.created_announcement_id}")
                else:
                    print(f"⚠️ Could not delete test announcement: HTTP {response.status_code}")
            except Exception as e:
                print(f"⚠️ Exception deleting test announcement: {str(e)}")
                
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("MULTI-CHANNEL COMMUNICATION TESTING SUMMARY")
        print("="*80)
        
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
            
            if failed > 0:
                print("  Failed Tests:")
                for detail in results["details"]:
                    if detail["status"] == "❌ FAIL":
                        print(f"    - {detail['test']}: {detail['message']}")
        
        print(f"\n{'='*80}")
        print(f"OVERALL RESULTS:")
        print(f"✅ Total Passed: {total_passed}")
        print(f"❌ Total Failed: {total_failed}")
        print(f"📊 Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%" if (total_passed + total_failed) > 0 else "0.0%")
        print("="*80)
        
    def run_all_tests(self):
        """Run all multi-channel communication tests"""
        print("🚀 Starting Multi-Channel Communication Features Testing...")
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
            
        # Run all test suites
        self.test_enhanced_multi_channel_salary_slip_sharing()
        self.test_digital_salary_slip_with_signature()
        self.test_company_announcement_multi_channel_sharing()
        self.test_hr_notification_system()
        self.test_communication_configuration()
        self.test_communication_testing()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print summary
        self.print_summary()

if __name__ == "__main__":
    tester = MultiChannelCommunicationTester()
    tester.run_all_tests()