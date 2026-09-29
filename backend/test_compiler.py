import os
import re
import unicodedata
import markdown
from bs4 import BeautifulSoup
from io import BytesIO

# Core ReportLab typesetting elements
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

# 1. SIMULATION TEXT: This mimics your exact resume text string layer
# We intentionally include non-breaking spaces and Markdown tokens to test our fixes
sample_cv_text = """
# Gal Peter

Phone: 0545732437 | Email: G.peter26@gmail.com | LinkedIn: ://linkedin.com

## Summary
QA Engineer with 19+ years of experience in software testing, both automated and manual. Well\xa0versed in SDLC, STLC, and QA Methodologies. Experienced in leading a QA team and managing software integration.

## Professional Experience
### QA Specialist, Plasson Ltd (2022 - 2025)
- Developed and maintained automated test suites using Python on TestComplete and Playwright.
- Planned, Created, and executed Manual tests for the in\u200bhouse MES system.
- Streamlined label creation process by managing a cloud-based solution.
"""

def test_pdf_compile(text_input, output_filename="Sandbox_Resume.pdf"):
    print("🚀 Initializing localized typographic compilation test pass...")
    
    # ADVANCED CLEANER LAYER: Converts non-breaking spaces and handles symbols safely
    # This is the line that will wipe out the black squares!
    clean = text_input.replace('\xa0', ' ').replace('\u200b', '').replace('\xad', '')
    clean = unicodedata.normalize('NFKC', clean)
    clean = clean.replace('█', '').replace('■', '').replace('●', '').replace('•', '')
    
    # Translate Markdown tokens to native ReportLab inline bold HTML elements
    clean = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean)
    clean = re.sub(r'\*(.*?)\*', r'<i>\1</i>', clean)
    
    # Compile Markdown block layers to HTML structures
    raw_html = markdown.markdown(clean)
    soup = BeautifulSoup(raw_html, "html.parser")
    
    doc = SimpleDocTemplate(output_filename, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    # Establish distinct typography definitions for clean presentation hierarchy
    body_style = ParagraphStyle('CV_Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=15, textColor='#374151', spaceAfter=5)
    h1_style = ParagraphStyle('CV_H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22, leading=26, textColor='#111827', spaceAfter=8, alignment=1)
    h2_style = ParagraphStyle('CV_H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor='#1e40af', spaceBefore=12, spaceAfter=6, keepWithNext=True)
    h3_style = ParagraphStyle('CV_H3', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor='#111827', spaceBefore=8, spaceAfter=4, keepWithNext=True)

    story = []
    
    for element in soup.children:
        if not element.name:
            continue
            
        inner_content = "".join([str(child) for child in element.children]).strip() or element.get_text().strip()
        
        if element.name == 'h1':
            story.append(Paragraph(inner_content, h1_style))
            story.append(Spacer(1, 4))
        elif element.name == 'h2':
            story.append(Paragraph(inner_content, h2_style))
        elif element.name == 'h3':
            story.append(Paragraph(inner_content, h3_style))
        elif element.name == 'p':
            story.append(Paragraph(inner_content, body_style))
        elif element.name in ['ul', 'ol']:
            list_items = []
            for li in element.find_all('li'):
                li_html = "".join([str(c) for c in li.children]).strip() or li.get_text().strip()
                if li_html:
                    list_items.append(ListItem(Paragraph(li_html, body_style), leftIndent=12, bulletOffsetY=-1))
            if list_items:
                story.append(ListFlowable(list_items, bulletType='bullet', start='circle', bulletFontName='Helvetica', bulletFontSize=5, leftIndent=8, spaceAfter=6))
                
    try:
        doc.build(story)
        print(f"✅ Success! Localized test document generated cleanly: {os.path.abspath(output_filename)}")
    except Exception as e:
        print(f"❌ Layout Compilation Error encountered: {str(e)}")

if __name__ == "__main__":
    test_pdf_compile(sample_cv_text)
