from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime, timezone
import io
import base64
from logo_watermark_generator import (
    create_watermarked_document, 
    create_professional_header_with_logo, 
    create_professional_footer,
    enhance_document_styling,
    get_professional_table_style
)

# Removed old header function - now using professional header from logo_watermark_generator

def generate_offer_letter_content(employee_data):
    """Generate offer letter content for watermarked document"""
    # Get enhanced professional styles
    styles = enhance_document_styling()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
        spaceAfter=20
    )
    
    # Build document content
    story = []
    
    # Company header
    story.extend(create_company_header(styles))
    
    # Date
    current_date = datetime.now(timezone.utc).strftime('%B %d, %Y')
    story.append(Paragraph(f'Date: {current_date}', date_style))
    
    # Title
    story.append(Paragraph('<b>OFFER LETTER</b>', title_style))
    
    # Employee details
    story.append(Paragraph(f'Dear {employee_data["full_name"]},', styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Offer content
    offer_content = f'''
    We are pleased to offer you the position of <b>{employee_data["designation"]}</b> in the <b>{employee_data["department"]}</b> department at Vishwas World Tech Private Limited.
    <br/><br/>
    <b>Position Details:</b><br/>
    • Designation: {employee_data["designation"]}<br/>
    • Department: {employee_data["department"]}<br/>
    • Employee ID: {employee_data["employee_id"]}<br/>
    • Reporting Manager: {employee_data.get("manager", "To be assigned")}<br/>
    • Joining Date: {datetime.fromisoformat(employee_data["join_date"].replace('Z', '+00:00')).strftime('%B %d, %Y') if isinstance(employee_data["join_date"], str) else employee_data["join_date"].strftime('%B %d, %Y')}<br/>
    <br/>
    <b>Compensation Package:</b><br/>
    • Basic Salary: ₹{employee_data["basic_salary"]:,.2f} per month<br/>
    • HRA: ₹{employee_data["basic_salary"] * 0.4:,.2f} per month (40% of basic)<br/>
    • DA: ₹{employee_data["basic_salary"] * 0.1:,.2f} per month (10% of basic)<br/>
    • Gross Salary: ₹{employee_data["basic_salary"] * 1.5:,.2f} per month<br/>
    <br/>
    <b>Terms and Conditions:</b><br/>
    • This offer is subject to verification of your credentials and background check.<br/>
    • You will be on probation for the first 6 months from your joining date.<br/>
    • Standard company policies regarding leave, working hours, and code of conduct will apply.<br/>
    • This offer is valid for 15 days from the date of this letter.<br/>
    <br/>
    We are excited about the possibility of you joining our team and contributing to Vishwas World Tech's growth and success.
    <br/><br/>
    Please confirm your acceptance by signing and returning a copy of this letter along with the required documents.
    '''
    
    story.append(Paragraph(offer_content, styles['Normal']))
    story.append(Spacer(1, 24))
    
    # Signature section
    signature_table = Table([
        ['Sincerely,', ''],
        ['', 'Acceptance:'],
        ['', ''],
        ['HR Manager', 'Employee Signature'],
        ['Vishwas World Tech Pvt Ltd', f'{employee_data["full_name"]}'],
        ['', f'Date: _______________']
    ], colWidths=[3*inch, 3*inch])
    
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(signature_table)
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data and encode to base64
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return base64.b64encode(pdf_data).decode()

def generate_appointment_letter(employee_data):
    """Generate appointment letter PDF for employee"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
        spaceAfter=20
    )
    
    # Build document content
    story = []
    
    # Company header
    story.extend(create_company_header(styles))
    
    # Date
    current_date = datetime.now(timezone.utc).strftime('%B %d, %Y')
    story.append(Paragraph(f'Date: {current_date}', date_style))
    
    # Title
    story.append(Paragraph('<b>APPOINTMENT LETTER</b>', title_style))
    
    # Employee details
    story.append(Paragraph(f'Dear {employee_data["full_name"]},', styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Appointment content
    appointment_content = f'''
    We are pleased to confirm your appointment as <b>{employee_data["designation"]}</b> in the <b>{employee_data["department"]}</b> department at Vishwas World Tech Private Limited, effective from {datetime.fromisoformat(employee_data["join_date"].replace('Z', '+00:00')).strftime('%B %d, %Y') if isinstance(employee_data["join_date"], str) else employee_data["join_date"].strftime('%B %d, %Y')}.
    <br/><br/>
    <b>Employment Details:</b><br/>
    • Employee ID: {employee_data["employee_id"]}<br/>
    • Designation: {employee_data["designation"]}<br/>
    • Department: {employee_data["department"]}<br/>
    • Reporting Manager: {employee_data.get("manager", "To be assigned")}<br/>
    • Employment Type: Full-time, Permanent<br/>
    • Work Location: Vishwas World Tech Corporate Office, Bangalore<br/>
    <br/>
    <b>Compensation and Benefits:</b><br/>
    • Basic Salary: ₹{employee_data["basic_salary"]:,.2f} per month<br/>
    • House Rent Allowance (HRA): ₹{employee_data["basic_salary"] * 0.4:,.2f} per month<br/>
    • Dearness Allowance (DA): ₹{employee_data["basic_salary"] * 0.1:,.2f} per month<br/>
    • Gross Monthly Salary: ₹{employee_data["basic_salary"] * 1.5:,.2f}<br/>
    • Provident Fund (PF): 12% of basic salary (employee + employer contribution)<br/>
    • Employee State Insurance (ESI): 1.75% of gross salary (if applicable)<br/>
    • Professional Tax (PT): As per state regulations<br/>
    <br/>
    <b>Terms of Employment:</b><br/>
    • Probation Period: 6 months from the date of joining<br/>
    • Working Hours: 9:00 AM to 6:00 PM, Monday to Friday<br/>
    • Annual Leave: 21 days per year (pro-rated basis)<br/>
    • Notice Period: 30 days (during probation), 60 days (post confirmation)<br/>
    • Medical Insurance: Group health insurance as per company policy<br/>
    <br/>
    <b>Responsibilities and Conduct:</b><br/>
    • You are expected to maintain the highest standards of professional conduct<br/>
    • Adherence to company policies, procedures, and code of conduct<br/>
    • Confidentiality of company information and trade secrets<br/>
    • Regular attendance and punctuality<br/>
    • Achievement of assigned targets and objectives<br/>
    <br/>
    Your employment with the company is subject to satisfactory completion of probation period and continued satisfactory performance.
    <br/><br/>
    We welcome you to the Vishwas World Tech family and look forward to your valuable contribution to our organization's growth and success.
    '''
    
    story.append(Paragraph(appointment_content, styles['Normal']))
    story.append(Spacer(1, 24))
    
    # Signature section
    signature_table = Table([
        ['For Vishwas World Tech Pvt Ltd,', 'Employee Acknowledgment:'],
        ['', ''],
        ['', ''],
        ['HR Manager', f'{employee_data["full_name"]}'],
        ['Name: _______________', 'Signature: _______________'],
        ['Date: _______________', 'Date: _______________']
    ], colWidths=[3*inch, 3*inch])
    
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(signature_table)
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data and encode to base64
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return base64.b64encode(pdf_data).decode()