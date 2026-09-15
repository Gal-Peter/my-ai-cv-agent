import fitz  # PyMuPDF
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load local environment variables from our secure .env file
load_dotenv()

# Verify that the Groq Key is actively recognized by the system container
if not os.getenv("GROQ_API_KEY"):
    print("⚠️ WARNING: GROQ_API_KEY is missing from environment variables. Please check your backend/.env configuration.")

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI(title="AI CV Agent Orchestrator API")

# Configure CORS so your React Vite container can securely send data streams
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Groq Brain Engine using the updated active free-tier model ID
agent_brain = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2
)

# In-memory session store to preserve the current uploaded CV text context
session_store = {"current_cv_text": ""}


class ChatMessage(BaseModel):
    message: str


@app.get("/")
async def root():
    """Health check endpoint for our automated pipelines and hosting layers."""
    return {"status": "healthy", "agent": "CV Optimizer with GPT-OSS Brain"}


@app.post("/api/upload")
async def upload_cv(file: UploadFile = File(...)):
    """
    Accepts PDF files, extracts bidirectional text cleanly,
    and returns both a short log preview and the complete text string.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        file_bytes = await file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        extracted_text_list = []
        for page in doc:
            # Standard block reading text extraction to avoid infinite loops on BiDi markers
            page_text = page.get_text("text") 
            if page_text:
                extracted_text_list.append(page_text)
                
        doc.close()
        
        # Merge individual pages into a single cohesive string
        full_text = "\n".join(extracted_text_list).strip()
        
        if not full_text:
            raise HTTPException(status_code=422, detail="PDF layer is empty or scanned. Please use a text-based PDF.")
            
        # Store the complete, un-truncated text inside the session store for the Groq agent
        session_store["current_cv_text"] = full_text
        
        print(f"✅ Successfully parsed {file.filename}! Total length: {len(full_text)} characters.")
        
        return {
            "filename": file.filename,
            "status": "parsed",
            "character_count": len(full_text),
            "text_preview": full_text[:300],  # Short visual snippet for the left chat bubbles
            "full_parsed_text": full_text     # The complete, uncut text payload for the right resume window
        }
    except Exception as e:
        print(f"❌ Critical Parsing Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@app.post("/api/chat")
async def chat_with_agent(payload: ChatMessage):
    """Processes user chat prompts against the uploaded CV data using the Groq Llama 3 model."""
    cv_data = session_store.get("current_cv_text", "")
    
    if not cv_data:
        return {
            "status": "waiting",
            "agent_response": "I see you want to optimize your resume! Please upload a PDF CV file using the upload block first so I can analyze your professional history."
        }
        
    # Build out a multi-step recruiter persona prompt boundary
    system_prompt = (
        "You are an expert bilingual technical recruiter specializing in Applicant Tracking Systems (ATS).\n"
        "Your task is to review the user's raw extracted CV text and modify it based on their request.\n\n"
        "CRITICAL RULES:\n"
        "1. You must maintain strict facts. Do not invent fake company names or jobs.\n"
        "2. If the text is in Hebrew, maintain flawless Hebrew syntax and format logic.\n"
        "3. Output your response using clean, professional Markdown syntax. Do not include chat boilerplates like 'Here is your resume:' or 'Sure, I can help with that.'\n"
        "4. Start directly with the Markdown layout document structure (e.g., # Full Name).\n\n"
        "--- RAW EXTRACTED CV DATA START ---\n"
        "{cv_context}\n"
        "--- RAW EXTRACTED CV DATA END ---"
    )
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{user_instruction}")
    ])
    
    try:
        # Construct the execution chain and invoke the Groq cloud model
        chain = prompt_template | agent_brain
        response = chain.invoke({
            "cv_context": cv_data,
            "user_instruction": payload.message
        })
        
        return {
            "status": "success",
            "agent_response": response.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API Error: {str(e)}")
