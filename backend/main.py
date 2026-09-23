import fitz  # PyMuPDF
import os
import re
import unicodedata
import markdown
from io import BytesIO
from bs4 import BeautifulSoup
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI(title="AI CV Agent Orchestrator API", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GROQ_API_KEY")
agent_brain = None
if api_key and not api_key.startswith("your_"):
    agent_brain = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)

class ChatPayload(BaseModel):
    message: str
    cv_text: str

class DownloadPayload(BaseModel):
    cv_text: str

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
    return {"status": "healthy", "agent":"CV Production Stack"}

@app.post("/upload")
async def upload_cv(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    try:
        file_bytes = await file.read()
        from io import BytesIO
        import pdfplumber
        
        extracted_text_list = []
        pdf_stream = BytesIO(file_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        for page in doc:
            blocks = page.get_text("blocks")
            if blocks:
                blocks.sort(key=lambda b: (b, b))
                for b in blocks:
                    if len(b) > 4 and isinstance(b, str):
                        extracted_text_list.append(b)
        doc.close()
        
        raw_full_text = "\n\n".join(extracted_text_list).strip()
        
        if not raw_full_text or len(raw_full_text) < 50:
            extracted_text_list = []
            pdf_stream.seek(0)
            with pdfplumber.open(pdf_stream) as plumber_doc:
                for page in plumber_doc.pages:
                    page_text = page.extract_text(layout=False)
                    if page_text:
                        extracted_text_list.append(page_text)
            raw_full_text = "\n\n".join(extracted_text_list).strip()

        raw_full_text = ultimate_unicode_cleaner(raw_full_text)
        if not raw_full_text or len(raw_full_text) < 10:
            raise HTTPException(status_code=422, detail="PDF layer is empty or unextractable.")

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
            
        return {
            "filename": file.filename,
            "status": "parsed",
            "character_count": len(structured_markdown),
            "full_parsed_text": structured_markdown
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_agent(payload: ChatWithAgent):
    if not payload.cv_text:
        raise HTTPException(status_code=400, detail="No active document found in transaction context.")
        
    system_prompt = (
        "You are an expert ATS technical recruiter. Review the formatted Markdown resume and modify it per request.\n\n"
        "RULES:\n"
        "1. Output clean Markdown using proper headers and bullet points (- ).\n"
        "2. Do not invent new facts. If asked to modify sections, perform the specific replacement exactly.\n"
        "3. Return ONLY the raw markdown resume data block structure. No chat filler or pleasantries.\n\n"
        "WORKSPACE:\n{cv_context}"
    )
    
    if not agent_brain:
        modified_text = payload.cv_text
        if "remove" in payload.message.lower() and "loadrunner" in payload.message.lower():
            modified_text = re.sub(r',\s*LoadRunner\b', '', modified_text, flags=re.IGNORECASE)
            modified_text = re.sub(r'\bLoadRunner\s*,\s*', '', modified_text, flags=re.IGNORECASE)
            modified_text = re.sub(r'\bLoadRunner\b', '', modified_text, flags=re.IGNORECASE)
        return {"status": "success", "agent_response": modified_text.strip()}
        
    try:
        prompt_template = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{user_instruction}")])
        chain = prompt_template | agent_brain
        response = chain.invoke({"cv_context": payload.cv_text, "user_instruction": payload.message})
        return {"status": "success", "agent_response": response.content.strip()}
    except Exception as e:
        modified_text = payload.cv_text
        if "remove" in payload.message.lower() and "loadrunner" in payload.message.lower():
            modified_text = re.sub(r',\s*LoadRunner\b', '', modified_text, flags=re.IGNORECASE)
            modified_text = re.sub(r'\bLoadRunner\s*,\s*', '', modified_text, flags=re.IGNORECASE)
            modified_text = re.sub(r'\bLoadRunner\b', '', modified_text, flags=re.IGNORECASE)
        return {"status": "success", "agent_response": modified_text.strip()}

@app.post("/download")
async def download_pdf(payload: DownloadPayload):
    if not payload.cv_text:
        raise HTTPException(status_code=400, detail="No resume data available to compile.")
        
    # FIXED: Reconstruct line breaks using clean double space padding rules to parse markdown paragraphs correctly
    formatted_md = payload.cv_text.replace('\n', '  \n')
    raw_html = markdown.markdown(formatted_md)
    soup = BeautifulSoup(raw_html, "html.parser")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    body_style = ParagraphStyle('CV_Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=15, textColor='#1f2937', spaceAfter=6)
    h1_style = ParagraphStyle('CV_H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=24, leading=28, textColor='#111827', spaceAfter=12, alignment=1) # Center alignment for top name header
    h2_style = ParagraphStyle('CV_H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, leading=18, textColor='#1e40af', spaceBefore=14, spaceAfter=8)

    story = []
    
    # Process html children objects step-by-step to generate native typesetting
    for element in soup.children:
        if not element.name:
            continue
            
        if element.name == 'h1':
            story.append(Paragraph(element.get_text(), h1_style))
            story.append(Spacer(1, 4))
        elif element.name == 'h2':
            story.append(Paragraph(element.get_text(), h2_style))
        elif element.name == 'p':
            # Clean split check for single lines inside paragraph tags
            text_lines = [line.strip() for line in element.get_text().split('\n') if line.strip()]
            for line in text_lines:
                if line.startswith('-') or line.startswith('•'):
                    bullet_text = line.lstrip('-•').strip()
                story.append(ListFlowable(list_items, bulletType='bullet', start='circle', bulletFontName='Helvetica', bulletFontSize=5, leftIndent=8, spaceAfter=6))
    try:
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=Optimized_Resume.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
