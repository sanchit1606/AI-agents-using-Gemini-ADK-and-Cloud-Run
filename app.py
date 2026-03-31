from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from dotenv import load_dotenv
import os
from pathlib import Path

from schemas import AnalyzeRequest, AnalyzeResponse
from agent import ErrorInterpreterAgent

# Load environment variables
load_dotenv()

# Check for API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY environment variable not set")

# Initialize FastAPI app
app = FastAPI(
    title="Error Interpreter Agent",
    description="AI-powered error analysis and resolution",
    version="1.0.0"
)

# Initialize the agent
agent = ErrorInterpreterAgent(api_key=api_key, model=os.getenv("GEMINI_MODEL"))

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the interactive UI"""
    index_path = Path(__file__).resolve().parent / "index.html"
    html_bytes = index_path.read_bytes()
    return Response(content=html_bytes, media_type="text/html; charset=utf-8")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_error(request: AnalyzeRequest):
    """Analyze an error message and return structured explanation"""
    try:
        result = await agent.analyze(request.error_text)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/info")
async def info():
    """Basic info endpoint"""
    return {"message": "Error Interpreter Agent is running. POST to /analyze or visit / for UI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
