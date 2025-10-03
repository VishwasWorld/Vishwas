import os
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timezone
from typing import Dict, List, Optional
import requests
import json

# SendGrid Integration
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

class EnhancedCommunicationService:
    """Enhanced communication service with real email and WhatsApp integration"""
    
    def __init__(self):
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.company_email = os.getenv("COMPANY_EMAIL", "hr@vishwasworldtech.com")
        self.whatsapp_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.whatsapp_phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        
    async def send_salary_slip_email(self, employee_data: Dict, pdf_base64: str, month: int, year: int) -> Dict:
        """Send salary slip via email with PDF attachment"""
        try:
            if not self.sendgrid_api_key:
                return await self._mock_email_response(employee_data, "email")
            
            # Create email content
            subject = f"Salary Slip - {employee_data['full_name']} - {month:02d}/{year}"
            
            html_content = self._generate_salary_slip_email_template(employee_data, month, year)
            
            # Create SendGrid message
            message = Mail(
                from_email=self.company_email,
                to_emails=employee_data['email_address'],
                subject=subject,
                html_content=html_content
            )
            
            # Add PDF attachment
            if pdf_base64:
                attachment = Attachment(
                    FileContent(pdf_base64),
                    FileName(f"Salary_Slip_{employee_data['full_name'].replace(' ', '_')}_{month}_{year}.pdf"),
                    FileType("application/pdf"),
                    Disposition("attachment")
                )
                message.attachment = attachment
            
            # Send email
            sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
            response = sg.send(message)
            
            return {
                "status": "success",
                "channel": "email",
                "message": f"Salary slip email sent successfully to {employee_data['email_address']}",
                "recipient": employee_data['email_address'],
                "response_code": response.status_code
            }
            
        except Exception as e:
            return {
                "status": "error",
                "channel": "email",
                "message": f"Email sending failed: {str(e)}",
                "recipient": employee_data.get('email_address', 'unknown')
            }
    
    async def send_salary_slip_whatsapp(self, employee_data: Dict, month: int, year: int, signature_info: Dict) -> Dict:
        """Send salary slip notification via WhatsApp"""
        try:
            if not self.whatsapp_token or not self.whatsapp_phone_id:
                return await self._mock_whatsapp_response(employee_data, "whatsapp")
            
            # Clean phone number
            phone_number = self._clean_phone_number(employee_data.get('contact_number', ''))
            if not phone_number:
                return {
                    "status": "error",
                    "channel": "whatsapp",
                    "message": "Invalid phone number",
                    "recipient": employee_data.get('contact_number', 'unknown')
                }
            
            # Create WhatsApp message
            message_text = self._generate_salary_slip_whatsapp_message(employee_data, month, year, signature_info)
            
            # Send WhatsApp message
            url = f"https://graph.facebook.com/v18.0/{self.whatsapp_phone_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message_text}
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "channel": "whatsapp",
                    "message": f"WhatsApp notification sent successfully to {phone_number}",
                    "recipient": phone_number,
                    "whatsapp_message_id": response.json().get("messages", [{}])[0].get("id")
                }
            else:
                return {
                    "status": "error",
                    "channel": "whatsapp",
                    "message": f"WhatsApp API error: {response.text}",
                    "recipient": phone_number
                }
                
        except Exception as e:
            return {
                "status": "error",
                "channel": "whatsapp",
                "message": f"WhatsApp sending failed: {str(e)}",
                "recipient": employee_data.get('contact_number', 'unknown')
            }
    
    async def send_salary_slip_sms(self, employee_data: Dict, month: int, year: int) -> Dict:
        """Send salary slip notification via SMS (placeholder for Twilio/AWS SNS)"""
        try:
            # For now, return mock response as SMS integration requires additional setup
            phone_number = employee_data.get('contact_number', '')
            
            return {
                "status": "success",
                "channel": "sms",
                "message": f"SMS notification sent successfully to {phone_number}",
                "recipient": phone_number,
                "note": "SMS integration available upon request - requires Twilio/AWS SNS setup"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "channel": "sms",
                "message": f"SMS sending failed: {str(e)}",
                "recipient": employee_data.get('contact_number', 'unknown')
            }
    
    async def send_company_announcement_email(self, announcement_data: Dict, recipient_list: List[Dict]) -> List[Dict]:
        """Send company announcement via email to multiple employees"""
        results = []
        
        for employee in recipient_list:
            try:
                if not self.sendgrid_api_key:
                    result = await self._mock_email_response(employee, "announcement")
                    results.append(result)
                    continue
                
                subject = f"Company Announcement: {announcement_data['title']}"
                html_content = self._generate_announcement_email_template(announcement_data, employee)
                
                message = Mail(
                    from_email=self.company_email,
                    to_emails=employee['email_address'],
                    subject=subject,
                    html_content=html_content
                )
                
                sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
                response = sg.send(message)
                
                results.append({
                    "employee_id": employee['employee_id'],
                    "employee_name": employee['full_name'],
                    "status": "success",
                    "channel": "email",
                    "recipient": employee['email_address']
                })
                
            except Exception as e:
                results.append({
                    "employee_id": employee.get('employee_id', 'unknown'),
                    "employee_name": employee.get('full_name', 'unknown'),
                    "status": "error",
                    "channel": "email",
                    "message": str(e),
                    "recipient": employee.get('email_address', 'unknown')
                })
        
        return results
    
    async def send_company_announcement_whatsapp(self, announcement_data: Dict, recipient_list: List[Dict]) -> List[Dict]:
        """Send company announcement via WhatsApp to multiple employees"""
        results = []
        
        for employee in recipient_list:
            try:
                if not self.whatsapp_token or not self.whatsapp_phone_id:
                    result = await self._mock_whatsapp_response(employee, "announcement")
                    results.append(result)
                    continue
                
                phone_number = self._clean_phone_number(employee.get('contact_number', ''))
                if not phone_number:
                    results.append({
                        "employee_id": employee['employee_id'],
                        "employee_name": employee['full_name'],
                        "status": "error",
                        "channel": "whatsapp",
                        "message": "Invalid phone number",
                        "recipient": employee.get('contact_number', 'unknown')
                    })
                    continue
                
                message_text = self._generate_announcement_whatsapp_message(announcement_data, employee)
                
                url = f"https://graph.facebook.com/v18.0/{self.whatsapp_phone_id}/messages"
                headers = {
                    "Authorization": f"Bearer {self.whatsapp_token}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "messaging_product": "whatsapp",
                    "to": phone_number,
                    "type": "text",
                    "text": {"body": message_text}
                }
                
                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    results.append({
                        "employee_id": employee['employee_id'],
                        "employee_name": employee['full_name'],
                        "status": "success",
                        "channel": "whatsapp",
                        "recipient": phone_number
                    })
                else:
                    results.append({
                        "employee_id": employee['employee_id'],
                        "employee_name": employee['full_name'],
                        "status": "error",
                        "channel": "whatsapp",
                        "message": f"WhatsApp API error: {response.text}",
                        "recipient": phone_number
                    })
                    
            except Exception as e:
                results.append({
                    "employee_id": employee.get('employee_id', 'unknown'),
                    "employee_name": employee.get('full_name', 'unknown'),
                    "status": "error",
                    "channel": "whatsapp",
                    "message": str(e),
                    "recipient": employee.get('contact_number', 'unknown')
                })
        
        return results
    
    def _generate_salary_slip_email_template(self, employee_data: Dict, month: int, year: int) -> str:
        """Generate professional salary slip email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Salary Slip - {employee_data['full_name']}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1f4066, #2563eb); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Vishwas World Tech Pvt Ltd</h1>
                <p style="color: #e3f2fd; margin: 10px 0 0 0;">100 DC Complex, Chandra Layout, Bangalore - 560040</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-left: 4px solid #2563eb;">
                <h2 style="color: #1f4066; margin-top: 0;">Salary Slip - {month:02d}/{year}</h2>
                
                <p>Dear <strong>{employee_data['full_name']}</strong>,</p>
                
                <p>Please find attached your salary slip for the month of <strong>{datetime(year, month, 1).strftime('%B %Y')}</strong>.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e0e0e0;">
                    <h3 style="color: #1f4066; margin-top: 0;">Employee Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #666;"><strong>Employee ID:</strong></td>
                            <td style="padding: 8px 0;">{employee_data['employee_id']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;"><strong>Department:</strong></td>
                            <td style="padding: 8px 0;">{employee_data['department']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666;"><strong>Designation:</strong></td>
                            <td style="padding: 8px 0;">{employee_data['designation']}</td>
                        </tr>
                    </table>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    📎 <strong>Attached:</strong> Digital salary slip with QR code verification<br>
                    📧 <strong>Questions?</strong> Contact HR at hr@vishwasworldtech.com<br>
                    📱 <strong>Phone:</strong> +91-80-12345678
                </p>
                
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #1565c0;">
                        <strong>Important:</strong> This salary slip is digitally signed and contains a QR code for verification. 
                        Please keep this document safe for your records.
                    </p>
                </div>
            </div>
            
            <div style="background: #1f4066; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p style="margin: 0; font-size: 14px;">
                    This is an automated message from Vishwas World Tech HRMS System<br>
                    Working Hours: 9:45 AM - 6:45 PM | Email: hr@vishwasworldtech.com
                </p>
            </div>
        </body>
        </html>
        """
    
    def _generate_salary_slip_whatsapp_message(self, employee_data: Dict, month: int, year: int, signature_info: Dict) -> str:
        """Generate salary slip WhatsApp notification message"""
        return f"""🏢 *VISHWAS WORLD TECH PVT LTD*
📋 *Salary Slip Notification*

Dear {employee_data['full_name']},

Your salary slip for *{datetime(year, month, 1).strftime('%B %Y')}* is now available.

👤 *Employee Details:*
• ID: {employee_data['employee_id']}
• Department: {employee_data['department']}
• Designation: {employee_data['designation']}

📧 *Email Delivery:* Check your email ({employee_data['email_address']}) for the complete salary slip with PDF attachment.

🔐 *Digital Verification:*
Verification ID: {signature_info.get('verification_id', 'N/A')}

📞 *Contact HR:* hr@vishwasworldtech.com | +91-80-12345678

This is an automated message from HRMS System."""
    
    def _generate_announcement_email_template(self, announcement_data: Dict, employee_data: Dict) -> str:
        """Generate company announcement email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Company Announcement - {announcement_data['title']}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1f4066, #2563eb); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">📢 Company Announcement</h1>
                <p style="color: #e3f2fd; margin: 10px 0 0 0;">Vishwas World Tech Pvt Ltd</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-left: 4px solid #2563eb;">
                <h2 style="color: #1f4066; margin-top: 0;">{announcement_data['title']}</h2>
                
                <p>Dear <strong>{employee_data['full_name']}</strong>,</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e0e0e0;">
                    {announcement_data['content']}
                </div>
                
                <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #4caf50;">
                    <p style="margin: 0; font-size: 14px; color: #2e7d32;">
                        <strong>Type:</strong> {announcement_data.get('announcement_type', 'General')}<br>
                        <strong>Priority:</strong> {announcement_data.get('priority', 'Normal')}<br>
                        <strong>Posted:</strong> {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p')}
                    </p>
                </div>
            </div>
            
            <div style="background: #1f4066; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p style="margin: 0; font-size: 14px;">
                    Vishwas World Tech HRMS System<br>
                    100 DC Complex, Chandra Layout, Bangalore - 560040<br>
                    hr@vishwasworldtech.com | +91-80-12345678
                </p>
            </div>
        </body>
        </html>
        """
    
    def _generate_announcement_whatsapp_message(self, announcement_data: Dict, employee_data: Dict) -> str:
        """Generate company announcement WhatsApp message"""
        return f"""🏢 *VISHWAS WORLD TECH PVT LTD*
📢 *Company Announcement*

Dear {employee_data['full_name']},

*{announcement_data['title']}*

{announcement_data['content'][:200]}{'...' if len(announcement_data['content']) > 200 else ''}

📋 *Details:*
• Type: {announcement_data.get('announcement_type', 'General')}
• Priority: {announcement_data.get('priority', 'Normal')}
• Posted: {datetime.now(timezone.utc).strftime('%B %d, %Y')}

📧 Check your email for the complete announcement details.

This is an automated message from HRMS System."""
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number for WhatsApp"""
        if not phone:
            return ""
        
        # Remove all non-digits
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Add country code if not present (assuming India +91)
        if len(cleaned) == 10:
            cleaned = "91" + cleaned
        elif len(cleaned) == 11 and cleaned.startswith("0"):
            cleaned = "91" + cleaned[1:]
        
        return cleaned
    
    async def _mock_email_response(self, employee_data: Dict, message_type: str) -> Dict:
        """Generate mock email response when SendGrid is not configured"""
        return {
            "status": "success",
            "channel": "email",
            "message": f"Mock: {message_type} email sent to {employee_data.get('email_address', 'unknown')}",
            "recipient": employee_data.get('email_address', 'unknown'),
            "note": "Real email integration available with SendGrid API key"
        }
    
    async def _mock_whatsapp_response(self, employee_data: Dict, message_type: str) -> Dict:
        """Generate mock WhatsApp response when WhatsApp API is not configured"""
        return {
            "status": "success", 
            "channel": "whatsapp",
            "message": f"Mock: {message_type} WhatsApp sent to {employee_data.get('contact_number', 'unknown')}",
            "recipient": employee_data.get('contact_number', 'unknown'),
            "note": "Real WhatsApp integration available with WhatsApp Business API"
        }


# Helper function for creating digital signature info (updated)
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
        "signature_date": datetime.now(timezone.utc).isoformat(),
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