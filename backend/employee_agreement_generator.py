from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime, timezone
import io
import base64
import requests
from PIL import Image as PILImage
from logo_watermark_generator import (
    create_watermarked_document, 
    create_professional_header_with_logo, 
    create_professional_footer,
    enhance_document_styling,
    get_professional_table_style
)

def download_and_process_logo():
    """Download company logo and prepare for PDF"""
    try:
        logo_url = "https://customer-assets.emergentagent.com/job_vishwas-hrms/artifacts/o6uun6ue_IMG-20251002-WA0067.jpg"
        response = requests.get(logo_url)
        
        if response.status_code == 200:
            # Save logo temporarily
            with open('/tmp/company_logo.jpg', 'wb') as f:
                f.write(response.content)
            return '/tmp/company_logo.jpg'
    except Exception as e:
        print(f"Error downloading logo: {e}")
    
    return None

def create_company_header_with_logo(styles):
    """Create company letterhead with logo"""
    story = []
    
    # Try to add logo
    logo_path = download_and_process_logo()
    if logo_path:
        try:
            # Create table with logo and company info
            logo_img = Image(logo_path, width=1*inch, height=1*inch)
            company_info = [
                Paragraph('<b><font size="16">VISHWAS WORLD TECH PRIVATE LIMITED</font></b>', styles['Title']),
                Paragraph('<font size="10">100 DC Complex, Chandra Layout, Bangalore - 560040</font>', styles['Normal']),
                Paragraph('<font size="10">Phone: +91-80-12345678 | Email: hr@vishwasworldtech.com</font>', styles['Normal'])
            ]
            
            # Create header table
            header_data = [[logo_img, company_info]]
            header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
            ]))
            
            story.append(header_table)
        except Exception as e:
            # Fallback without logo
            story.append(Paragraph('<b>VISHWAS WORLD TECH PRIVATE LIMITED</b>', styles['Title']))
            story.append(Paragraph('100 DC Complex, Chandra Layout, Bangalore - 560040', styles['Normal']))
            story.append(Paragraph('Phone: +91-80-12345678 | Email: hr@vishwasworldtech.com', styles['Normal']))
    else:
        # Fallback without logo
        story.append(Paragraph('<b>VISHWAS WORLD TECH PRIVATE LIMITED</b>', styles['Title']))
        story.append(Paragraph('100 DC Complex, Chandra Layout, Bangalore - 560040', styles['Normal']))
        story.append(Paragraph('Phone: +91-80-12345678 | Email: hr@vishwasworldtech.com', styles['Normal']))
    
    story.append(Spacer(1, 12))
    story.append(Paragraph('<hr width="100%" color="blue"/>', styles['Normal']))
    story.append(Spacer(1, 12))
    
    return story

def generate_employee_agreement_content(employee_data):
    """Generate employee agreement content for watermarked document"""
    # Get enhanced professional styles
    styles = enhance_document_styling()
    
    # Enhanced justify style for legal content
    justify_style = ParagraphStyle(
        'JustifyStyle',
        parent=styles['ProfessionalBody'],
        alignment=TA_JUSTIFY,
        fontSize=11,
        spaceAfter=8
    )
    
    # Build document content
    story = []
    
    # Professional company header with logo
    story.extend(create_professional_header_with_logo(styles))
    
    # Title
    story.append(Paragraph('<b>EMPLOYEE AGREEMENT</b>', title_style))
    story.append(Spacer(1, 20))
    
    # Date and employee info
    current_date = datetime.now(timezone.utc).strftime('%B %d, %Y')
    
    employee_info_data = [
        ['Employee Name:', employee_data['full_name'], 'Employee ID:', employee_data['employee_id']],
        ['Department:', employee_data['department'], 'Designation:', employee_data['designation']],
        ['Date of Agreement:', current_date, 'Effective Date:', datetime.fromisoformat(employee_data["join_date"].replace('Z', '+00:00')).strftime('%B %d, %Y') if isinstance(employee_data["join_date"], str) else employee_data["join_date"].strftime('%B %d, %Y')]
    ]
    
    emp_table = Table(employee_info_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(emp_table)
    story.append(Spacer(1, 20))
    
    # Agreement content
    agreement_text = f'''
    This Employment Agreement ("Agreement") is entered into between Vishwas World Tech Private Limited, a company incorporated under the Companies Act, 2013, having its registered office at 100 DC Complex, Chandra Layout, Bangalore - 560040 (hereinafter referred to as "Company") and {employee_data["full_name"]} (hereinafter referred to as "Employee").
    <br/><br/>
    WHEREAS, the Company desires to employ the services of the Employee, and the Employee agrees to be employed by the Company subject to the terms and conditions set forth herein.
    <br/><br/>
    NOW, THEREFORE, in consideration of the mutual covenants and agreements contained herein, the parties agree as follows:
    '''
    
    story.append(Paragraph(agreement_text, justify_style))
    story.append(Spacer(1, 15))
    
    # Terms and Conditions
    story.append(Paragraph('<b>TERMS AND CONDITIONS OF EMPLOYMENT</b>', section_style))
    
    # 1. Position and Duties
    story.append(Paragraph('<b>1. POSITION AND DUTIES</b>', styles['Heading4']))
    position_text = f'''
    1.1. The Employee shall serve the Company as {employee_data["designation"]} in the {employee_data["department"]} department.
    <br/>
    1.2. The Employee shall perform duties as assigned by the Company and shall devote full time, attention, and efforts to the business of the Company.
    <br/>
    1.3. The Employee shall report to {employee_data.get("manager", "the designated supervisor")} or such other person as may be designated by the Company.
    '''
    story.append(Paragraph(position_text, justify_style))
    story.append(Spacer(1, 10))
    
    # 2. Working Hours and Attendance Policy
    story.append(Paragraph('<b>2. WORKING HOURS AND ATTENDANCE POLICY</b>', styles['Heading4']))
    working_hours_text = '''
    2.1. <b>Standard Working Hours:</b> The Employee shall work from <b>9:45 AM to 6:45 PM</b>, Monday through Friday, with a lunch break as designated by the Company.
    <br/>
    2.2. <b>Attendance Requirements:</b> The Employee is required to maintain regular attendance and punctuality. Location-based attendance tracking is mandatory for all employees.
    <br/>
    2.3. <b>Late Login Policy:</b> 
    <br/>&nbsp;&nbsp;&nbsp;• Employees logging in after 9:45 AM will be marked as late.
    <br/>&nbsp;&nbsp;&nbsp;• <b>Salary Deductions for Late Login:</b>
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Up to 15 minutes late: No deduction (grace period)
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- 16-30 minutes late: ₹200 deduction per occurrence
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- 31-60 minutes late: ₹500 deduction per occurrence
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- More than 60 minutes late: ₹1,000 deduction per occurrence
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- More than 3 late arrivals per month: Additional ₹1,500 deduction
    <br/>
    2.4. <b>Attendance Tracking:</b> All attendance will be tracked through the Company's HRMS system with GPS location verification.
    '''
    story.append(Paragraph(working_hours_text, justify_style))
    story.append(Spacer(1, 10))
    
    # 3. Compensation and Benefits
    story.append(Paragraph('<b>3. COMPENSATION AND BENEFITS</b>', styles['Heading4']))
    compensation_text = f'''
    3.1. <b>Basic Salary:</b> The Employee shall receive a basic salary of ₹{employee_data["basic_salary"]:,.2f} per month.
    <br/>
    3.2. <b>Allowances:</b>
    <br/>&nbsp;&nbsp;&nbsp;• House Rent Allowance (HRA): 50% of basic salary (Metro rate for Bangalore)
    <br/>&nbsp;&nbsp;&nbsp;• Dearness Allowance (DA): 10% of basic salary
    <br/>&nbsp;&nbsp;&nbsp;• Medical Allowance: ₹1,250 per month
    <br/>&nbsp;&nbsp;&nbsp;• Transport Allowance: ₹1,600 per month
    <br/>
    3.3. <b>Statutory Deductions:</b>
    <br/>&nbsp;&nbsp;&nbsp;• Provident Fund (PF): 12% of basic salary (employee contribution)
    <br/>&nbsp;&nbsp;&nbsp;• Employee State Insurance (ESI): 1.75% of gross salary (if applicable)
    <br/>&nbsp;&nbsp;&nbsp;• Professional Tax: As per Karnataka state regulations
    <br/>&nbsp;&nbsp;&nbsp;• Income Tax: As per Income Tax Act, 1961
    <br/>
    3.4. <b>Salary Processing:</b> Salary will be calculated based on actual attendance and processed monthly.
    '''
    story.append(Paragraph(compensation_text, justify_style))
    story.append(Spacer(1, 10))
    
    # 4. Probation Period
    story.append(Paragraph('<b>4. PROBATION PERIOD</b>', styles['Heading4']))
    probation_text = '''
    4.1. The Employee shall be on probation for a period of <b>6 (six) months</b> from the date of joining.
    <br/>
    4.2. During probation, either party may terminate this agreement by giving <b>30 days written notice</b>.
    <br/>
    4.3. Upon satisfactory completion of probation, the Employee shall be confirmed as a permanent employee.
    '''
    story.append(Paragraph(probation_text, justify_style))
    story.append(Spacer(1, 10))
    
    # 5. Confidentiality and Non-Disclosure
    story.append(Paragraph('<b>5. CONFIDENTIALITY AND NON-DISCLOSURE</b>', styles['Heading4']))
    confidentiality_text = '''
    5.1. The Employee agrees to maintain strict confidentiality regarding all proprietary information, trade secrets, client data, and business processes of the Company.
    <br/>
    5.2. The Employee shall not disclose any confidential information to third parties during and after the term of employment.
    <br/>
    5.3. All intellectual property developed during employment shall belong exclusively to the Company.
    '''
    story.append(Paragraph(confidentiality_text, justify_style))
    story.append(Spacer(1, 10))
    
    # 6. Code of Conduct
    story.append(Paragraph('<b>6. CODE OF CONDUCT</b>', styles['Heading4']))
    conduct_text = '''
    6.1. The Employee shall maintain the highest standards of professional conduct and ethics.
    6.2. The Employee shall comply with all Company policies, procedures, and applicable laws.
    6.3. The Employee shall not engage in any activity that conflicts with the interests of the Company.
    6.4. Violation of the code of conduct may result in disciplinary action, including termination.
    '''
    story.append(Paragraph(conduct_text, justify_style))
    story.append(Spacer(1, 10))
    
    # 7. Termination
    story.append(Paragraph('<b>7. TERMINATION</b>', styles['Heading4']))
    termination_text = '''
    7.1. <b>During Probation:</b> Either party may terminate with 30 days notice.
    <br/>
    7.2. <b>Post Confirmation:</b> Either party may terminate with 60 days written notice.
    <br/>
    7.3. <b>Immediate Termination:</b> The Company may terminate immediately for gross misconduct, breach of confidentiality, or violation of company policies.
    <br/>
    7.4. <b>Notice Pay:</b> Payment in lieu of notice may be made at the Company's discretion.
    '''
    story.append(Paragraph(termination_text, justify_style))
    story.append(Spacer(1, 10))
    
    # 8. Governing Law
    story.append(Paragraph('<b>8. GOVERNING LAW AND JURISDICTION</b>', styles['Heading4']))
    law_text = '''
    8.1. This Agreement shall be governed by the laws of India and the State of Karnataka.
    <br/>
    8.2. Any disputes arising from this Agreement shall be subject to the exclusive jurisdiction of courts in Bangalore, Karnataka.
    <br/>
    8.3. This Agreement supersedes all previous agreements and constitutes the entire agreement between the parties.
    '''
    story.append(Paragraph(law_text, justify_style))
    story.append(Spacer(1, 20))
    
    # Acceptance and Signatures
    story.append(Paragraph('<b>ACCEPTANCE AND SIGNATURES</b>', section_style))
    
    acceptance_text = '''
    By signing below, both parties acknowledge that they have read, understood, and agree to be bound by all the terms and conditions of this Employment Agreement.
    '''
    story.append(Paragraph(acceptance_text, justify_style))
    story.append(Spacer(1, 20))
    
    # Signature table
    signature_table = Table([
        ['FOR VISHWAS WORLD TECH PVT LTD', 'EMPLOYEE ACCEPTANCE'],
        ['', ''],
        ['', ''],
        ['_______________________', '_______________________'],
        ['Authorized Signatory', f'{employee_data["full_name"]}'],
        ['Name: HR Manager', f'Employee ID: {employee_data["employee_id"]}'],
        ['Date: _______________', 'Date: _______________'],
        ['', ''],
        ['Company Seal:', 'Witness:'],
        ['', ''],
        ['', '_______________________'],
        ['', 'Name & Signature']
    ], colWidths=[3*inch, 3*inch])
    
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEABOVE', (0, 3), (1, 3), 1, colors.black),
        ('LINEABOVE', (0, 10), (1, 10), 1, colors.black),
    ]))
    
    story.append(signature_table)
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Paragraph('This is a legally binding document. Please read carefully before signing.', 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, 
                                       textColor=colors.grey)))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data and encode to base64
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return base64.b64encode(pdf_data).decode()

def calculate_late_login_penalty(login_time_str, scheduled_time="09:45"):
    """
    Calculate penalty for late login based on company policy
    
    Args:
        login_time_str: Login time in HH:MM format
        scheduled_time: Scheduled login time (default 09:45)
    
    Returns:
        dict with penalty amount and details
    """
    try:
        from datetime import datetime, time
        
        # Parse times
        scheduled = datetime.strptime(scheduled_time, "%H:%M").time()
        actual = datetime.strptime(login_time_str, "%H:%M").time()
        
        # Convert to minutes for calculation
        scheduled_minutes = scheduled.hour * 60 + scheduled.minute
        actual_minutes = actual.hour * 60 + actual.minute
        
        # Calculate delay in minutes
        delay_minutes = actual_minutes - scheduled_minutes
        
        if delay_minutes <= 0:
            return {"penalty": 0, "delay_minutes": 0, "category": "On Time"}
        elif delay_minutes <= 15:
            return {"penalty": 0, "delay_minutes": delay_minutes, "category": "Grace Period"}
        elif delay_minutes <= 30:
            return {"penalty": 200, "delay_minutes": delay_minutes, "category": "16-30 minutes late"}
        elif delay_minutes <= 60:
            return {"penalty": 500, "delay_minutes": delay_minutes, "category": "31-60 minutes late"}
        else:
            return {"penalty": 1000, "delay_minutes": delay_minutes, "category": "More than 60 minutes late"}
            
    except Exception as e:
        return {"penalty": 0, "delay_minutes": 0, "category": "Error calculating penalty", "error": str(e)}