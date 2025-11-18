import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import EnhancedResearchAgent
import uvicorn
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Configuration for LLM
# -----------------------------
PRIMARY_LLM = "gemini"
FALLBACK_LLM = "groq"

PRIMARY_API_KEY = os.getenv("LLM_API_KEY")  # Gemini API key
FALLBACK_API_KEY = os.getenv("GROQ_API_KEY")  # Groq API key

# -----------------------------
# Initialize agent with fallback logic
# -----------------------------
try:
    # Try Gemini first
    agent = EnhancedResearchAgent(llm_type=PRIMARY_LLM, api_key=PRIMARY_API_KEY)
except Exception as e:
    print(f"Primary LLM ({PRIMARY_LLM}) failed: {str(e)}")
    # Fall back to Groq
    if FALLBACK_API_KEY:
        print(f"Falling back to {FALLBACK_LLM}")
        agent = EnhancedResearchAgent(llm_type=FALLBACK_LLM, api_key=FALLBACK_API_KEY)
    else:
        raise RuntimeError(f"Failed to initialize LLM agent: {str(e)}")

# -----------------------------
# Initialize FastAPI app
# -----------------------------
app = FastAPI(title="Agentic AI Backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Pydantic models
# -----------------------------
class QueryRequest(BaseModel):
    query: str
    max_iterations: int = 5

class QueryResponse(BaseModel):
    result: str
    steps: list
    status: str

# -----------------------------
# API endpoints
# -----------------------------
@app.get("/")
async def root():
    return {"message": "Agentic AI Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        result = await agent.run(request.query, request.max_iterations)
        return QueryResponse(
            result=result["final_answer"],
            steps=result["steps"],
            status="success"
        )
    except Exception as e:
        # If primary LLM fails mid-query, you could also implement fallback here
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
