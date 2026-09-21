import fitz  # PyMuPDF
import os
import re
import unicodedata
import markdown
from io import BytesIO
from bs4 import BeautifulSoup
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# ReportLab core typesetting elements
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# FIXED: Turn off redirect_slashes to prevent Google Cloud's proxies from throwing 404 errors
app = FastAPI(title="AI CV Agent Orchestrator API", redirect_slashes=False)

# PRODUCTION CORS OVERRIDE: Allow absolute public access for serverless requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Groq Engine safely checking environment bounds
api_key = os.getenv("GROQ_API_KEY")
agent_brain = None
if api_key and not api_key.startswith("your_"):
    agent_brain = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)
else:
    print("⚠️ DOCKER LOG WARNING: GROQ_API_KEY is missing or invalid.")

session_store = {"current_cv_text": ""}


class ChatMessage(BaseModel):
    message: str


def ultimate_unicode_cleaner(text_data):
    if not text_data:
        return ""
    clean = unicodedata.normalize('NFKC', text_data)
    clean = clean.replace('\xad', '').replace('\xa0', ' ').replace('\u200b', '')
    clean = clean.replace('█', '').replace('■', '').replace('●', '').replace('•', '')
    clean = re.sub(r'[^\x20-\x7E\u0590-\u05FF\n]', '', clean)
    clean = re.sub(r' +', ' ', clean)
    return clean


def fallback_clean_text(raw_text):
    if not raw_text:
        return ""
    clean = ultimate_unicode_cleaner(raw_text)
    lines = [line.strip() for line in clean.splitlines() if line.strip()]
    formatted_lines = []
    for line in lines:
        if any(sec in line for sec in ["Professional Experience", "Skills", "Education", "Contact", "Summary", "Professional Summary"]):
            formatted_lines.append(f"\n## {line}\n")
        elif "Gal Peter" in line:
            formatted_lines.append(f"# {line}\n")
        else:
            if " - " in line or ". " in line:
                sub_sentences = re.split(r'(?<=\.)\s+|\s+-\s+', line)
                for sentence in sub_sentences:
                    s_clean = sentence.strip().lstrip('-').strip()
                    if s_clean and len(s_clean) > 10:
                        formatted_lines.append(f"- {s_clean}")
            elif len(line) > 30 and not line.endswith(":") and not "|" in line:
                formatted_lines.append(f"- {line}")
            else:
                formatted_lines.append(line)
    return "\n".join(formatted_lines).strip()


@app.get("/")
async def root():
    return {"status": "healthy", "agent": "CV Production Stack"}


# FIXED: Standardized direct base path strings without trailing slashes
@app.post("/upload")
async def upload_cv(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    try:
        file_bytes = await file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        extracted_text_list = []
        for page in doc:
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: (b, b))
            for b in blocks:
                block_text = b
                if block_text and isinstance(block_text, str):
                    block_text = ultimate_unicode_cleaner(block_text)
                    clean_block = "\n".join([line.strip() for line in block_text.splitlines() if line.strip()])
                    extracted_text_list.append(clean_block)
        doc.close()
        raw_full_text = "\n\n".join(extracted_text_list).strip()
        if not raw_full_text:
            raise HTTPException(status_code=422, detail="PDF text layer is empty or scanned.")

        if agent_brain:
            try:
                structuring_prompt = (
                    "You are an expert ATS layout parser. Re-write this resume text into clean, structured Markdown format.\n\n"
                    "CRITICAL RULES:\n"
                    "1. Every single job responsibility line under companies MUST start with a hyphen and space ('- ').\n"
                    "2. Clean formatting glitches like split words ('in-house') or space breaks in phone digits.\n"
                    "3. Return ONLY the markdown resume text layer. No introductory boilerplates.\n\n"
                    "RAW CV INPUT:\n{raw_text}"
                )
                prompt_template = ChatPromptTemplate.from_messages([("system", structuring_prompt)])
                chain = prompt_template | agent_brain
                response = chain.invoke({"raw_text": raw_full_text})
                structured_markdown = response.content.strip()
            except Exception:
                structured_markdown = fallback_clean_text(raw_full_text)
        else:
            structured_markdown = fallback_clean_text(raw_full_text)
            
        session_store["current_cv_text"] = structured_markdown
        return {
            "filename": file.filename,
            "status": "parsed",
            "character_count": len(structured_markdown),
            "text_preview": structured_markdown[:300],
            "full_parsed_text": structured_markdown
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.post("/upload/")
async def upload_cv(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        # Read the raw incoming binary stream completely
        file_bytes = await file.read()
        
        # FIXED: Wrap the raw bytes inside a BytesIO memory buffer block to ensure PyMuPDF can seek the text layers
        from io import BytesIO
        pdf_stream = BytesIO(file_bytes)
        
        # Open the document using the stream buffer map layout
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        extracted_text_list = []
        
        for page in doc:
            # First attempt: Collect text block matrix units sequential layout
            blocks = page.get_text("blocks")
            
            if blocks:
                blocks.sort(key=lambda b: (b[1], b[0]))  # Standard vertical top-to-bottom sort
                for b in blocks:
                    block_text = b[4].strip() if len(b) > 4 else ""
                    if block_text:
                        block_text = ultimate_unicode_cleaner(block_text)
                        clean_block = "\n".join([line.strip() for line in block_text.splitlines() if line.strip()])
                        extracted_text_list.append(clean_block)
            else:
                # FALLBACK BACKUP: If block arrays return empty spaces, scrape the direct page string characters natively
                page_text = page.get_text("text")
                if page_text:
                    extracted_text_list.append(ultimate_unicode_cleaner(page_text))
                    
        doc.close()
        raw_full_text = "\n\n".join(extracted_text_list).strip()
        
        # Log active metric status traces straight into your Cloud Run console panel logs
        print(f"📦 DEBUG CONTAINER LOG: Successfully extracted {len(raw_full_text)} characters from file stream.")
        
        if not raw_full_text:
            # If the layer is still empty, the resume is an image snapshot (scanned document)
            raise HTTPException(status_code=422, detail="PDF text layer is empty. Scanned documents/images are not supported yet.")

        if agent_brain:
            try:
                structuring_prompt = (
                    "You are an expert ATS layout parser. Re-write this resume text into clean, structured Markdown format.\n\n"
                    "CRITICAL RULES:\n"
                    "1. Every single job responsibility line under companies MUST start with a hyphen and space ('- ').\n"
                    "2. Clean formatting glitches like split words ('in-house') or space breaks in phone digits.\n"
                    "3. Return ONLY the markdown resume text layer. No introductory boilerplates.\n\n"
                    "RAW CV INPUT:\n{raw_text}"
                )
                prompt_template = ChatPromptTemplate.from_messages([("system", structuring_prompt)])
                chain = prompt_template | agent_brain
                response = chain.invoke({"raw_text": raw_full_text})
                structured_markdown = response.content.strip()
            except Exception:
                structured_markdown = fallback_clean_text(raw_full_text)
        else:
            structured_markdown = fallback_clean_text(raw_full_text)
            
        session_store["current_cv_text"] = structured_markdown
        return {
            "filename": file.filename,
            "status": "parsed",
            "character_count": len(structured_markdown),
            "text_preview": structured_markdown[:300],
            "full_parsed_text": structured_markdown
        }
    except Exception as e:
        print(f"❌ Internal Processing Crash inside upload pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download")
async def download_pdf():
    md_content = session_store.get("current_cv_text", "")
    if not md_content:
        raise HTTPException(status_code=400, detail="No resume data available.")
    clean_md = ultimate_unicode_cleaner(md_content)
    raw_html = markdown.markdown(clean_md)
    soup = BeautifulSoup(raw_html, "html.parser")
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle('CV_Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=15, textColor='#1f2937', spaceAfter=4)
    h1_style = ParagraphStyle('CV_H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=24, leading=28, textColor='#111827', spaceAfter=12)
    h2_style = ParagraphStyle('CV_H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, leading=18, textColor='#1e40af', spaceBefore=16, spaceAfter=8)

    story = []
    for element in soup.children:
        if element.name == 'h1':
            story.append(Paragraph(element.get_text(), h1_style))
            story.append(Spacer(1, 4))
        elif element.name == 'h2':
            story.append(Paragraph(element.get_text(), h2_style))
        elif element.name == 'p':
            story.append(Paragraph(element.get_text(), body_style))
        elif element.name in ['ul', 'ol']:
            list_items = []
            for li in element.find_all('li'):
                text = li.get_text().strip()
                if text.startswith("-") or text.startswith("•"):
                    text = text[1:].strip()
                if text:
                    list_items.append(ListItem(Paragraph(text, body_style), leftIndent=12, bulletOffsetY=-1))
            if list_items:
                story.append(ListFlowable(list_items, bulletType='bullet', start='circle', bulletFontName='Helvetica', bulletFontSize=5, leftIndent=8, spaceAfter=6))
    try:
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=Optimized_Resume.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    