from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io

def json_to_pdf(data: dict) -> bytes:
    # Mapping from JSON keys to human-readable labels
    key_labels = {
        "name": "Name",
        "age": "Age",
        "gender": "Gender",
        "address": "Address",
        "chief_complaint": "Chief Complaint",
        "symptom_duration": "Symptom Duration",
        "symptom_frequency": "Symptom Frequency",
        "medical_history": "Medical History",
        "surgical_history": "Surgical History",
        "current_medications": "Current Medications",
        "allergies": "Allergies",
        "region": "Region",
        "partner_name": "Partner's Name",
        "partner_age": "Partner's Age",
        "pregnancies": "Number of Pregnancies",
        "deliveries": "Number of Deliveries",
        "miscarriages": "Number of Miscarriages",
        "menstrual_cycle_regular": "Is Menstrual Cycle Regular",
        "last_period": "Start of Last Period",
        "previous_treatments": "Previous Treatments, If Any",
        "family_history": "Family History",
        "lifestyle": "Lifestyle",
        "diet": "Diet",
        "exercise": "Exercise",
        "sleep_pattern": "Sleeping Habits",
        "stress_levels": "Stress Level",
        "smoking": "Smoke",
        "drinking": "Drink"
    }

    # Create a bytes buffer
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get default styles and create custom ones
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        leftIndent=0
    )
    
    subsection_style = ParagraphStyle(
        'SubsectionHeader',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=15,
        fontName='Helvetica-Bold',
        leftIndent=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        fontName='Helvetica',
        leftIndent=0
    )
    
    indented_style = ParagraphStyle(
        'IndentedNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        fontName='Helvetica',
        leftIndent=20
    )
    
    # Story array to hold flowables
    story = []
    
    # Add title
    story.append(Paragraph("IVF Patient Intake Summary", title_style))
    story.append(Spacer(1, 20))
    
    def add_content(key, value, indent_level=0):
        """Recursively add content to the story"""
        # Determine the label
        label = key_labels.get(key, key.replace('_', ' ').title())
        
        if isinstance(value, dict):
            # This is a section header
            if indent_level == 0:
                story.append(Paragraph(f"<b>{label}</b>", section_style))
            else:
                story.append(Paragraph(f"<b>{label}</b>", subsection_style))
            
            # Add nested items
            for subkey, subval in value.items():
                add_content(subkey, subval, indent_level + 1)
        else:
            # This is a key-value pair
            # Clean up the value for display
            clean_value = str(value) if value is not None else "Not specified"
            
            # Create the formatted text
            text = f"<b>{label}:</b> {clean_value}"
            
            # Choose style based on indent level
            if indent_level > 0:
                story.append(Paragraph(text, indented_style))
            else:
                story.append(Paragraph(text, normal_style))
    
    # Process all data
    for key, value in data.items():
        add_content(key, value)
    
    # Build the PDF
    doc.build(story)
    
    # Get the PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes