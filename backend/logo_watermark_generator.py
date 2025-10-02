from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime, timezone
import io
import base64
import requests
from PIL import Image as PILImage
import os

class LogoWatermarkCanvas(canvas.Canvas):
    """Custom canvas class to add watermark to every page"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.logo_path = self.download_and_process_logo()
        
    def download_and_process_logo(self):
        """Download and process company logo"""
        try:
            logo_url = "https://customer-assets.emergentagent.com/job_vishwas-hrms/artifacts/o6uun6ue_IMG-20251002-WA0067.jpg"
            response = requests.get(logo_url)
            
            if response.status_code == 200:
                # Save logo temporarily
                with open('/tmp/watermark_logo.jpg', 'wb') as f:
                    f.write(response.content)
                return '/tmp/watermark_logo.jpg'
        except Exception as e:
            print(f"Error downloading logo for watermark: {e}")
        return None
    
    def showPage(self):
        """Add watermark to each page before showing"""
        self.add_watermark()
        canvas.Canvas.showPage(self)
    
    def add_watermark(self):
        """Add logo watermark to the page"""
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                # Save current graphics state
                self.saveState()
                
                # Set transparency for watermark
                self.setFillAlpha(0.1)  # Very transparent
                
                # Calculate center position
                page_width, page_height = A4
                center_x = page_width / 2
                center_y = page_height / 2
                
                # Draw watermark logo in center
                logo_width = 4 * inch
                logo_height = 4 * inch
                
                self.drawImage(
                    self.logo_path,
                    center_x - logo_width/2,
                    center_y - logo_height/2,
                    width=logo_width,
                    height=logo_height,
                    mask='auto',
                    preserveAspectRatio=True
                )
                
                # Add "VISHWAS WORLD TECH" text watermark
                self.setFont("Helvetica-Bold", 48)
                self.setFillColor(colors.lightgrey)
                self.setFillAlpha(0.05)
                
                # Rotate and draw company name
                self.saveState()
                self.translate(center_x, center_y - 100)
                self.rotate(45)
                text_width = self.stringWidth("VISHWAS WORLD TECH", "Helvetica-Bold", 48)
                self.drawString(-text_width/2, 0, "VISHWAS WORLD TECH")
                self.restoreState()
                
                # Restore graphics state
                self.restoreState()
                
            except Exception as e:
                print(f"Error adding watermark: {e}")
                self.restoreState()

def download_and_process_logo():
    """Download company logo and prepare for PDF"""
    try:
        logo_url = "https://customer-assets.emergentagent.com/job_vishwas-hrms/artifacts/o6uun6ue_IMG-20251002-WA0067.jpg"
        response = requests.get(logo_url)
        
        if response.status_code == 200:
            # Save logo temporarily
            with open('/tmp/company_logo_header.jpg', 'wb') as f:
                f.write(response.content)
            return '/tmp/company_logo_header.jpg'
    except Exception as e:
        print(f"Error downloading logo: {e}")
    
    return None

def create_professional_header_with_logo(styles):
    """Create professional company header with logo and styling"""
    story = []
    
    # Try to add logo
    logo_path = download_and_process_logo()
    if logo_path:
        try:
            # Create professional header with logo and company info
            logo_img = Image(logo_path, width=1.5*inch, height=1.5*inch)
            
            # Company information with enhanced styling
            company_info = [
                Paragraph('<b><font size="20" color="darkblue">VISHWAS WORLD TECH PRIVATE LIMITED</font></b>', styles['Title']),
                Paragraph('<font size="11" color="darkblue">100 DC Complex, Chandra Layout, Bangalore - 560040</font>', styles['Normal']),
                Paragraph('<font size="10" color="darkblue">Phone: +91-80-12345678 | Email: hr@vishwasworldtech.com</font>', styles['Normal']),
                Paragraph('<font size="10" color="darkblue">Website: www.vishwasworldtech.com | GST: 29ABCDE1234F1Z5</font>', styles['Normal'])
            ]
            
            # Create professional header table with styling
            header_data = [[logo_img, company_info]]
            header_table = Table(header_data, colWidths=[2*inch, 5*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
                ('BOX', (0, 0), (-1, -1), 2, colors.darkblue),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ]))
            
            story.append(header_table)
        except Exception as e:
            # Fallback header
            story.append(Paragraph('<b><font size="18" color="darkblue">VISHWAS WORLD TECH PRIVATE LIMITED</font></b>', styles['Title']))
            story.append(Paragraph('100 DC Complex, Chandra Layout, Bangalore - 560040', styles['Normal']))
            story.append(Paragraph('Phone: +91-80-12345678 | Email: hr@vishwasworldtech.com', styles['Normal']))
    else:
        # Fallback header
        story.append(Paragraph('<b><font size="18" color="darkblue">VISHWAS WORLD TECH PRIVATE LIMITED</font></b>', styles['Title']))
        story.append(Paragraph('100 DC Complex, Chandra Layout, Bangalore - 560040', styles['Normal']))
        story.append(Paragraph('Phone: +91-80-12345678 | Email: hr@vishwasworldtech.com', styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Professional separator line
    story.append(Paragraph('<hr width="100%" color="darkblue" size="3"/>', styles['Normal']))
    story.append(Spacer(1, 15))
    
    return story

def create_professional_footer(styles):
    """Create professional footer with company branding"""
    footer_content = [
        Spacer(1, 30),
        Paragraph('<hr width="100%" color="darkblue" size="2"/>', styles['Normal']),
        Spacer(1, 10),
        Paragraph('<b><font size="8" color="darkblue">VISHWAS WORLD TECH PRIVATE LIMITED</font></b>', 
                 ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.darkblue)),
        Paragraph('<font size="7" color="grey">This is a computer-generated document and does not require physical signature.</font>', 
                 ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER, textColor=colors.grey)),
        Paragraph('<font size="7" color="grey">For any queries, please contact HR Department at hr@vishwasworldtech.com</font>', 
                 ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER, textColor=colors.grey)),
    ]
    return footer_content

def enhance_document_styling():
    """Create enhanced styling for professional documents"""
    styles = getSampleStyleSheet()
    
    # Custom styles for professional documents
    styles.add(ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=22,
        spaceAfter=25,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=colors.darkblue,
        borderPadding=8,
        backColor=colors.lightblue
    ))
    
    styles.add(ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=colors.lightgrey,
        borderPadding=5,
        backColor=colors.lightgrey
    ))
    
    styles.add(ParagraphStyle(
        'ProfessionalBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        textColor=colors.black,
        fontName='Helvetica'
    ))
    
    return styles

def create_watermarked_document(content_generator_func, *args, **kwargs):
    """
    Create a document with watermark using custom canvas
    
    Args:
        content_generator_func: Function that generates document content
        *args, **kwargs: Arguments to pass to the content generator
    
    Returns:
        base64 encoded PDF with watermark
    """
    buffer = io.BytesIO()
    
    # Use custom canvas with watermark
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=0.5*inch, 
        bottomMargin=0.5*inch,
        canvasmaker=LogoWatermarkCanvas
    )
    
    # Generate document content
    story = content_generator_func(*args, **kwargs)
    
    # Build PDF with watermark
    doc.build(story)
    
    # Get PDF data and encode to base64
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return base64.b64encode(pdf_data).decode()

# Professional table styles
def get_professional_table_style():
    """Get standardized professional table styling"""
    return TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        
        # Body styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        
        # Border styling
        ('GRID', (0, 0), (-1, -1), 1, colors.darkblue),
        ('BOX', (0, 0), (-1, -1), 2, colors.darkblue),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ])