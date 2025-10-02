from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime, timezone
import io
import base64
import requests
from logo_watermark_generator import create_watermarked_document, download_and_process_logo

def generate_standard_salary_slip_content(salary_calculation):
    """Generate standard format salary slip content"""
    # Get professional styles
    styles = getSampleStyleSheet()
    
    # Custom styles for standard salary slip
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontSize=16,
        fontName='Helvetica-Bold',
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        spaceAfter=5
    )
    
    address_style = ParagraphStyle(
        'AddressStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    # Build document content
    story = []
    
    # Company Header with Logo
    logo_path = download_and_process_logo()
    if logo_path:
        try:
            # Create header with logo and company info
            logo_img = Image(logo_path, width=1.2*inch, height=1.2*inch)
            
            company_info = [
                Paragraph('<b>VISHWAS WORLD TECH PRIVATE LIMITED</b>', company_style),
                Paragraph('100 DC Complex, Chandra Layout, Bangalore - 560040', address_style),
                Paragraph('Phone: +91-80-12345678 | Email: hr@vishwasworldtech.com', address_style),
            ]
            
            header_data = [[logo_img, company_info]]
            header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
            ]))
            
            story.append(header_table)
        except:
            # Fallback header
            story.append(Paragraph('<b>VISHWAS WORLD TECH PRIVATE LIMITED</b>', company_style))
            story.append(Paragraph('100 DC Complex, Chandra Layout, Bangalore - 560040', address_style))
    else:
        story.append(Paragraph('<b>VISHWAS WORLD TECH PRIVATE LIMITED</b>', company_style))
        story.append(Paragraph('100 DC Complex, Chandra Layout, Bangalore - 560040', address_style))
    
    story.append(Spacer(1, 15))
    
    # Title
    story.append(Paragraph('<b>SALARY SLIP</b>', header_style))
    
    # Employee and Pay Period Information
    emp_info = salary_calculation['employee_info']
    current_month = emp_info['calculation_month']
    
    # Employee details table
    emp_details_data = [
        ['Employee Name:', emp_info['employee_name'], 'Employee ID:', emp_info['employee_id']],
        ['Department:', emp_info['department'], 'Designation:', emp_info['designation']],
        ['Pay Period:', current_month, 'Payment Date:', datetime.now().strftime('%d-%m-%Y')]
    ]
    
    emp_details_table = Table(emp_details_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    emp_details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(emp_details_table)
    story.append(Spacer(1, 20))
    
    # Attendance Summary
    emp_details = salary_calculation['employee_details']
    attendance_data = [
        ['ATTENDANCE SUMMARY', '', '', ''],
        ['Total Working Days', str(emp_details['total_working_days']), 'Present Days', str(emp_details['present_days'])],
        ['Absent Days', str(emp_details['total_working_days'] - emp_details['present_days']), 'Attendance %', f"{emp_details['attendance_percentage']:.1f}%"]
    ]
    
    attendance_table = Table(attendance_data, colWidths=[1.8*inch, 1.6*inch, 1.8*inch, 1.6*inch])
    attendance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('SPAN', (0, 0), (3, 0)),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(attendance_table)
    story.append(Spacer(1, 20))
    
    # Salary Details - Standard Format
    earnings = salary_calculation['earnings']
    deductions = salary_calculation['deductions']
    
    # Earnings Section
    earnings_data = [
        ['EARNINGS', 'AMOUNT (₹)'],
        ['Basic Salary', f"{earnings['basic_salary']:,.2f}"],
        ['House Rent Allowance (HRA)', f"{earnings['hra']:,.2f}"],
        ['Dearness Allowance (DA)', f"{earnings['da']:,.2f}"],
        ['Medical Allowance', f"{earnings['medical_allowance']:,.2f}"],
        ['Transport Allowance', f"{earnings['transport_allowance']:,.2f}"],
        ['Special Allowance', f"{earnings['special_allowance']:,.2f}"],
        ['', ''],
        ['TOTAL EARNINGS', f"₹{earnings['gross_salary']:,.2f}"]
    ]
    
    # Deductions Section
    deductions_data = [
        ['DEDUCTIONS', 'AMOUNT (₹)'],
        ['Provident Fund (PF)', f"{deductions['pf_employee']:,.2f}"],
        ['Employee State Insurance (ESI)', f"{deductions['esi_employee']:,.2f}"],
        ['Professional Tax (PT)', f"{deductions['professional_tax']:,.2f}"],
        ['Income Tax (TDS)', f"{deductions['income_tax']:,.2f}"],
        ['', ''],
        ['', ''],
        ['', ''],
        ['TOTAL DEDUCTIONS', f"₹{deductions['total_deductions']:,.2f}"]
    ]
    
    # Combined Salary Table
    salary_data = []
    for i in range(len(earnings_data)):
        row = earnings_data[i] + deductions_data[i]
        salary_data.append(row)
    
    salary_table = Table(salary_data, colWidths=[2.2*inch, 1.3*inch, 2.2*inch, 1.3*inch])
    salary_table.setStyle(TableStyle([
        # Headers
        ('BACKGROUND', (0, 0), (1, 0), colors.darkgreen),
        ('BACKGROUND', (2, 0), (3, 0), colors.darkred),
        ('TEXTCOLOR', (0, 0), (3, 0), colors.white),
        ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (3, 0), 11),
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),
        
        # Body
        ('FONTNAME', (0, 1), (3, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (3, -2), 10),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        
        # Totals
        ('BACKGROUND', (0, -1), (1, -1), colors.lightgreen),
        ('BACKGROUND', (2, -1), (3, -1), colors.lightcoral),
        ('FONTNAME', (0, -1), (3, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (3, -1), 11),
        
        # Grid
        ('GRID', (0, 0), (3, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (3, -1), 8),
        ('BOTTOMPADDING', (0, 0), (3, -1), 8),
    ]))
    
    story.append(salary_table)
    story.append(Spacer(1, 20))
    
    # Net Salary
    net_salary_data = [
        ['NET SALARY PAYABLE', f"₹{salary_calculation['net_salary']:,.2f}"]
    ]
    
    net_table = Table(net_salary_data, colWidths=[4.5*inch, 2.5*inch])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 2, colors.darkblue),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(net_table)
    story.append(Spacer(1, 30))
    
    # Digital Signature Section
    signature_data = [
        ['Digitally Generated on:', datetime.now().strftime('%d-%m-%Y at %I:%M %p'), 'Generated by:', 'HRMS System'],
        ['', '', '', ''],
        ['Authorized Signatory', 'Employee Acknowledgment', 'HR Department', 'System Verification'],
        ['(Digital Signature)', f'({emp_info["employee_name"]})', '(HR Manager)', '(Auto-Generated)']
    ]
    
    signature_table = Table(signature_data, colWidths=[1.75*inch, 1.75*inch, 1.75*inch, 1.75*inch])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.black),
    ]))
    
    story.append(signature_table)
    story.append(Spacer(1, 20))
    
    # Digital Signature Notice
    story.append(Paragraph(
        '<b>DIGITAL SIGNATURE APPLIED</b><br/>'
        'This salary slip has been digitally signed and generated by Vishwas World Tech HRMS System.<br/>'
        'No physical signature required. For verification, contact HR Department.',
        ParagraphStyle('DigitalNotice', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, 
                      textColor=colors.darkblue, fontName='Helvetica-Bold')
    ))
    
    # Footer
    story.append(Spacer(1, 15))
    story.append(Paragraph(
        'This is a computer-generated document and does not require physical signature.<br/>'
        'For any queries, please contact HR Department at hr@vishwasworldtech.com',
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER, textColor=colors.grey)
    ))
    
    return story

def generate_standard_salary_slip(salary_calculation):
    """Generate standard format salary slip with digital signature"""
    return create_watermarked_document(generate_standard_salary_slip_content, salary_calculation)