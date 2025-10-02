from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import base64

def generate_salary_slip(salary_calculation):
    """Generate salary slip PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    # Build document content
    story = []
    
    # Company header
    story.append(Paragraph('<b>VISHWAS WORLD TECH PRIVATE LIMITED</b>', title_style))
    story.append(Paragraph('Corporate Office: Technology Hub, Innovation District, Bangalore - 560001', styles['Normal']))
    story.append(Paragraph('Phone: +91-80-12345678 | Email: hr@vishwasworldtech.com', styles['Normal']))
    story.append(Spacer(1, 20))
    story.append(Paragraph('<hr width="100%" color="blue"/>', styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Salary slip title
    story.append(Paragraph('<b>SALARY SLIP</b>', header_style))
    story.append(Spacer(1, 15))
    
    # Employee details table
    emp_info = salary_calculation['employee_info']
    employee_details = [
        ['Employee ID:', emp_info['employee_id'], 'Employee Name:', emp_info['employee_name']],
        ['Department:', emp_info['department'], 'Designation:', emp_info['designation']],
        ['Month/Year:', emp_info['calculation_month'], 'Generated On:', datetime.now().strftime('%B %d, %Y')]
    ]
    
    emp_table = Table(employee_details, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(emp_table)
    story.append(Spacer(1, 20))
    
    # Attendance details
    emp_details = salary_calculation['employee_details']
    attendance_data = [
        ['Present Days:', str(emp_details['present_days']), 'Total Working Days:', str(emp_details['total_working_days'])],
        ['Absent Days:', str(emp_details['total_working_days'] - emp_details['present_days']), 
         'Attendance %:', f"{emp_details['attendance_percentage']}%"]
    ]
    
    attendance_table = Table(attendance_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    attendance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightyellow),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(Paragraph('<b>Attendance Details</b>', styles['Heading3']))
    story.append(attendance_table)
    story.append(Spacer(1, 20))
    
    # Salary breakdown table
    earnings = salary_calculation['earnings']
    deductions = salary_calculation['deductions']
    
    salary_data = [
        ['EARNINGS', 'AMOUNT (₹)', 'DEDUCTIONS', 'AMOUNT (₹)'],
        ['Basic Salary', f"{earnings['basic_salary']:,.2f}", 'PF (Employee)', f"{deductions['pf_employee']:,.2f}"],
        ['HRA', f"{earnings['hra']:,.2f}", 'ESI (Employee)', f"{deductions['esi_employee']:,.2f}"],
        ['DA', f"{earnings['da']:,.2f}", 'Professional Tax', f"{deductions['professional_tax']:,.2f}"],
        ['Medical Allowance', f"{earnings['medical_allowance']:,.2f}", 'Income Tax', f"{deductions['income_tax']:,.2f}"],
        ['Transport Allowance', f"{earnings['transport_allowance']:,.2f}", '', ''],
        ['Special Allowance', f"{earnings['special_allowance']:,.2f}", '', ''],
        ['', '', '', ''],
        ['GROSS SALARY', f"₹{earnings['gross_salary']:,.2f}", 'TOTAL DEDUCTIONS', f"₹{deductions['total_deductions']:,.2f}"],
    ]
    
    salary_table = Table(salary_data, colWidths=[2*inch, 1.5*inch, 2*inch, 1.5*inch])
    salary_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -3), 'Helvetica'),
        ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        
        # Total rows
        ('BACKGROUND', (0, -2), (-1, -1), colors.lightgrey),
        ('LINEABOVE', (0, -2), (-1, -2), 2, colors.black),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(Paragraph('<b>Salary Breakdown</b>', styles['Heading3']))
    story.append(salary_table)
    story.append(Spacer(1, 20))
    
    # Net salary
    net_salary_data = [
        ['NET SALARY PAYABLE', f"₹{salary_calculation['net_salary']:,.2f}"]
    ]
    
    net_table = Table(net_salary_data, colWidths=[4*inch, 2.5*inch])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('GRID', (0, 0), (-1, -1), 2, colors.darkgreen),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(net_table)
    story.append(Spacer(1, 30))
    
    # Employer contributions
    employer_contrib = salary_calculation['employer_contributions']
    story.append(Paragraph('<b>Employer Contributions</b>', styles['Heading3']))
    
    employer_data = [
        ['PF (Employer Contribution)', f"₹{employer_contrib['pf_employer']:,.2f}"],
        ['ESI (Employer Contribution)', f"₹{employer_contrib['esi_employer']:,.2f}"],
        ['Total Employer Contribution', f"₹{employer_contrib['total_employer_contribution']:,.2f}"]
    ]
    
    employer_table = Table(employer_data, colWidths=[4*inch, 2.5*inch])
    employer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -2), colors.lightblue),
        ('BACKGROUND', (0, -1), (-1, -1), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, -2), colors.black),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(employer_table)
    story.append(Spacer(1, 30))
    
    # Footer
    story.append(Paragraph('This is a computer-generated salary slip and does not require signature.', 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, 
                                       textColor=colors.grey)))
    story.append(Paragraph('For any queries, please contact HR Department.', 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, 
                                       textColor=colors.grey)))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF data and encode to base64
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return base64.b64encode(pdf_data).decode()