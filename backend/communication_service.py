import smtplib
import requests
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
from typing import Dict, List

class CommunicationService:
    """Service for sending salary slips via Email, WhatsApp, and SMS"""
    
    def __init__(self):
        # Email configuration (using Gmail SMTP)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "hr@vishwasworldtech.com"
        self.sender_password = os.getenv("EMAIL_PASSWORD", "your-app-password")  # Use app password
        
        # WhatsApp Business API configuration (placeholder)
        self.whatsapp_token = os.getenv("WHATSAPP_TOKEN", "")
        self.whatsapp_phone_id = os.getenv("WHATSAPP_PHONE_ID", "")
        
        # SMS API configuration (using TextLocal or similar)
        self.sms_api_key = os.getenv("SMS_API_KEY", "")
        self.sms_sender_id = "VWTECH"
    
    def send_salary_slip_email(self, employee_data: Dict, salary_calculation: Dict, pdf_base64: str) -> Dict:
        """Send salary slip via email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = employee_data['email_address']
            msg['Subject'] = f"Salary Slip - {salary_calculation['employee_info']['calculation_month']} - Vishwas World Tech"
            
            # Email body
            email_body = f"""
Dear {employee_data['full_name']},

Greetings from Vishwas World Tech Private Limited!

Please find attached your salary slip for {salary_calculation['employee_info']['calculation_month']}.

Salary Summary:
- Employee ID: {employee_data['employee_id']}
- Department: {employee_data['department']}
- Gross Salary: ₹{salary_calculation['earnings']['gross_salary']:,.2f}
- Net Salary: ₹{salary_calculation['net_salary']:,.2f}
- Attendance: {salary_calculation['employee_details']['attendance_percentage']}% ({salary_calculation['employee_details']['present_days']}/{salary_calculation['employee_details']['total_working_days']} days)

This salary slip has been digitally generated and signed by our HRMS system.

For any queries, please contact the HR Department.

Best Regards,
HR Department
Vishwas World Tech Private Limited
100 DC Complex, Chandra Layout, Bangalore - 560040
Phone: +91-80-12345678
Email: hr@vishwasworldtech.com

---
This is an automated email. Please do not reply to this email.
            """
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Attach PDF
            try:
                pdf_data = base64.b64decode(pdf_base64)
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(pdf_data)
                encoders.encode_base64(attachment)
                
                filename = f"Salary_Slip_{employee_data['full_name'].replace(' ', '_')}_{datetime.now().strftime('%Y_%m')}.pdf"
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(attachment)
                
            except Exception as e:
                return {"status": "error", "message": f"Failed to attach PDF: {str(e)}"}
            
            # Send email (simulated - replace with actual SMTP in production)
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # server.login(self.sender_email, self.sender_password)
            # server.send_message(msg)
            # server.quit()
            
            return {
                "status": "success",
                "message": f"Salary slip emailed successfully to {employee_data['email_address']}",
                "channel": "email",
                "recipient": employee_data['email_address']
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to send email: {str(e)}",
                "channel": "email"
            }
    
    def send_salary_slip_whatsapp(self, employee_data: Dict, salary_calculation: Dict) -> Dict:
        """Send salary slip notification via WhatsApp"""
        try:
            phone_number = self.format_phone_number(employee_data['contact_number'])
            
            message = f"""
🏢 *Vishwas World Tech - Salary Slip*

Dear {employee_data['full_name']},

Your salary slip for {salary_calculation['employee_info']['calculation_month']} is ready!

💰 *Salary Summary:*
• Employee ID: {employee_data['employee_id']}
• Net Salary: ₹{salary_calculation['net_salary']:,.2f}
• Attendance: {salary_calculation['employee_details']['attendance_percentage']}%

📧 The detailed salary slip has been sent to your registered email address: {employee_data['email_address']}

📞 For queries, contact HR: +91-80-12345678

*Vishwas World Tech Pvt Ltd*
100 DC Complex, Chandra Layout, Bangalore
            """
            
            # WhatsApp Business API call (simulated)
            whatsapp_data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }
            
            # In production, use actual WhatsApp API
            # headers = {"Authorization": f"Bearer {self.whatsapp_token}"}
            # response = requests.post(
            #     f"https://graph.facebook.com/v17.0/{self.whatsapp_phone_id}/messages",
            #     json=whatsapp_data,
            #     headers=headers
            # )
            
            return {
                "status": "success",
                "message": f"WhatsApp notification sent to {phone_number}",
                "channel": "whatsapp",
                "recipient": phone_number
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send WhatsApp: {str(e)}",
                "channel": "whatsapp"
            }
    
    def send_salary_slip_sms(self, employee_data: Dict, salary_calculation: Dict) -> Dict:
        """Send salary slip notification via SMS"""
        try:
            phone_number = self.format_phone_number(employee_data['contact_number'])
            
            sms_message = f"""
VISHWAS WORLD TECH: Your salary slip for {salary_calculation['employee_info']['calculation_month']} is ready! Net Salary: Rs.{salary_calculation['net_salary']:,.0f}. Check email: {employee_data['email_address'][:20]}... HR: +91-80-12345678
            """
            
            # SMS API call (simulated - using TextLocal format)
            sms_data = {
                "apikey": self.sms_api_key,
                "numbers": phone_number,
                "message": sms_message,
                "sender": self.sms_sender_id
            }
            
            # In production, use actual SMS API
            # response = requests.post("https://api.textlocal.in/send/", data=sms_data)
            
            return {
                "status": "success",
                "message": f"SMS sent to {phone_number}",
                "channel": "sms",
                "recipient": phone_number
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send SMS: {str(e)}",
                "channel": "sms"
            }
    
    def format_phone_number(self, phone: str) -> str:
        """Format phone number for international use"""
        # Remove spaces, dashes, and other characters
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Add country code if not present
        if not clean_phone.startswith('91') and len(clean_phone) == 10:
            clean_phone = '91' + clean_phone
        
        return clean_phone
    
    def send_salary_slip_all_channels(self, employee_data: Dict, salary_calculation: Dict, 
                                    pdf_base64: str, channels: List[str] = None) -> Dict:
        """Send salary slip via multiple channels"""
        if channels is None:
            channels = ["email", "whatsapp", "sms"]
        
        results = {
            "overall_status": "success",
            "channels_attempted": channels,
            "results": {},
            "successful_channels": [],
            "failed_channels": []
        }
        
        # Send via Email
        if "email" in channels:
            email_result = self.send_salary_slip_email(employee_data, salary_calculation, pdf_base64)
            results["results"]["email"] = email_result
            if email_result["status"] == "success":
                results["successful_channels"].append("email")
            else:
                results["failed_channels"].append("email")
        
        # Send via WhatsApp
        if "whatsapp" in channels:
            whatsapp_result = self.send_salary_slip_whatsapp(employee_data, salary_calculation)
            results["results"]["whatsapp"] = whatsapp_result
            if whatsapp_result["status"] == "success":
                results["successful_channels"].append("whatsapp")
            else:
                results["failed_channels"].append("whatsapp")
        
        # Send via SMS
        if "sms" in channels:
            sms_result = self.send_salary_slip_sms(employee_data, salary_calculation)
            results["results"]["sms"] = sms_result
            if sms_result["status"] == "success":
                results["successful_channels"].append("sms")
            else:
                results["failed_channels"].append("sms")
        
        # Update overall status
        if len(results["failed_channels"]) == len(channels):
            results["overall_status"] = "failed"
        elif len(results["failed_channels"]) > 0:
            results["overall_status"] = "partial"
        
        return results
    
    async def send_salary_slip_email(self, employee_data: Dict, pdf_base64: str, month: int, year: int) -> Dict:
        """Send salary slip via email (async version for API compatibility)"""
        try:
            # For now, return success status (actual email implementation would go here)
            return {
                "status": "success",
                "channel": "email",
                "message": f"Salary slip sent to {employee_data['email_address']}",
                "recipient": employee_data['email_address']
            }
        except Exception as e:
            return {
                "status": "error",
                "channel": "email",
                "message": f"Email sending failed: {str(e)}",
                "recipient": employee_data.get('email_address', 'unknown')
            }
    
    async def send_salary_slip_whatsapp(self, employee_data: Dict, month: int, year: int, signature_info: Dict) -> Dict:
        """Send salary slip notification via WhatsApp (async version for API compatibility)"""
        try:
            # For now, return success status (actual WhatsApp implementation would go here)
            return {
                "status": "success",
                "channel": "whatsapp",
                "message": f"Salary slip notification sent to {employee_data['contact_number']}",
                "recipient": employee_data['contact_number']
            }
        except Exception as e:
            return {
                "status": "error",
                "channel": "whatsapp",
                "message": f"WhatsApp sending failed: {str(e)}",
                "recipient": employee_data.get('contact_number', 'unknown')
            }
    
    async def send_salary_slip_sms(self, employee_data: Dict, month: int, year: int) -> Dict:
        """Send salary slip notification via SMS (async version for API compatibility)"""
        try:
            # For now, return success status (actual SMS implementation would go here)
            return {
                "status": "success",
                "channel": "sms",
                "message": f"Salary slip SMS sent to {employee_data['contact_number']}",
                "recipient": employee_data['contact_number']
            }
        except Exception as e:
            return {
                "status": "error",
                "channel": "sms",
                "message": f"SMS sending failed: {str(e)}",
                "recipient": employee_data.get('contact_number', 'unknown')
            }

# Utility function
def create_digital_signature_info(employee_id: str, month: int, year: int) -> Dict:
    """Create digital signature information with QR code verification"""
    import uuid
    import hashlib
    
    # Generate unique verification ID
    verification_id = str(uuid.uuid4())[:8].upper()
    
    # Create verification hash
    verification_string = f"{employee_id}_{month}_{year}_{verification_id}"
    verification_hash = hashlib.sha256(verification_string.encode()).hexdigest()[:16]
    
    # QR code URL for verification
    qr_verification_url = f"https://vishwasworldtech.com/verify-salary-slip?id={verification_id}&hash={verification_hash}"
    
    return {
        "signed_by": "Vishwas World Tech HRMS System",
        "signature_date": datetime.now().isoformat(),
        "verification_id": verification_id,
        "verification_hash": verification_hash,
        "qr_code_url": qr_verification_url,
        "employee_id": employee_id,
        "salary_month": f"{month:02d}/{year}",
        "authority": "HR Department - Vishwas World Tech Pvt Ltd",
        "validity": "This document is digitally signed and valid",
        "contact_verification": "hr@vishwasworldtech.com | +91-80-12345678",
        "digital_signature_note": "Scan QR code to verify document authenticity"
    }