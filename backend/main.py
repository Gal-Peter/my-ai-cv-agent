import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AI CV Agent Orchestrator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    message: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "CV Optimizer v1.0"}


@app.post("/api/upload")
async def upload_cv(file: UploadFile = File(...)):
    """Accepts PDF files, processes bidirectional text, and extracts raw text strings."""
    # Enforce file format constraints
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported at this stage.")
        
    try:
        # Read the uploaded file binary bytes directly into stream memory
        file_bytes = await file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        extracted_text = ""
        for page in doc:
            # PyMuPDF extracts text using internal BiDi layout engine rules
            extracted_text += page.get_text(sort=True) + "\n"
            
        doc.close()
        
        if not extracted_text.strip():
            raise HTTPException(status_code=422, detail="PDF text layer is empty or scanned. OCR required.")
            
        return {
            "filename": file.filename,
            "status": "parsed",
            "character_count": len(extracted_text),
            "text_preview": extracted_text[:300]  # Sends preview back to side-by-side pane
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@app.post("/api/chat")
async def chat_with_agent(payload: ChatMessage):
    """Placeholder endpoint for streaming agent responses."""
    return {"status": "success", "agent_response": f"Processed prompt: {payload.message}"}
