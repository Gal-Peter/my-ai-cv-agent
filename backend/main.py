from fastapi import FastAPI
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
    """Health check endpoint for our CI/CD pipeline and cloud hosts."""
    return {"status": "healthy", "agent": "CV Optimizer v1.0"}


@app.post("/api/chat")
async def chat_with_agent(payload: ChatMessage):
    """Placeholder endpoint for streaming our AI agent's reasoning loop."""
    return {
        "status": "success",
        "agent_response": f"Received: '{payload.message}'. Agent initializing...",
    }
