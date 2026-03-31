# Error Interpreter Agent - AI Agent using Gemini ADK and Cloud Run

A single AI agent built with Google ADK and Gemini that analyzes terminal errors and returns structured explanations with fixes. Hosted on Cloud Run as an HTTP service.

## Overview

This project implements a **Developer Error Interpreter Agent** that:
- ✅ Accepts error messages via HTTP API
- ✅ Uses Gemini AI to analyze and explain errors
- ✅ Returns structured JSON with error summary, root cause, and fix steps
- ✅ Deployed on Google Cloud Run
- ✅ Simple web UI for interactive testing

## Project Structure

```
├── app.py                      # FastAPI server & HTTP endpoints
├── agent.py                    # Error interpreter agent (ADK + Gemini)
├── schemas.py                  # Pydantic request/response models
├── index.html                  # Web UI for testing
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Cloud Run container
├── .env                        # API key configuration (local only)
├── README.md                   # This file
└── local-testing.md           # Local testing guide
```

## Features

- **Simple API**: `POST /analyze` endpoint for error analysis
- **ADK Integration**: Uses Google's AI Development Kit with Gemini
- **Structured Responses**: JSON with error details, fixes, and confidence level
- **Web UI**: Clean interface to paste errors and get explanations
- **Health Checks**: `/health` endpoint for monitoring
- **Cloud Run Ready**: Dockerfile and environment configuration included

## Live Deployment

The application is **live and running** on Google Cloud Run:

🔗 **Service URL:** https://ai-agents-gemini-604413037271.asia-south1.run.app/

- **Region:** asia-south1 (India)
- **Status:** ✅ Active
- **Try it now:** Visit the URL above or test the API endpoints

## Local Development

### Prerequisites
- Python 3.8+
- Conda/pip
- Google Gemini API key

### Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Create `.env` file** in project root:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

3. **Start the server**:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

4. **Access the UI**:
```
http://localhost:8000
```

See [`local-testing.md`](local-testing.md ) for detailed testing instructions.

## API Endpoints

### POST /analyze
Analyzes an error message and returns structured explanation.

**Request:**
```json
{
  "error_text": "ModuleNotFoundError: No module named requests"
}
```

**Response:**
```json
{
  "error_summary": "A required Python module 'requests' is not installed",
  "probable_cause": "The requests library was not installed in the current environment",
  "fix_steps": [
    "Install the requests library using pip",
    "Verify installation with: pip show requests"
  ],
  "commands": ["pip install requests"],
  "confidence": "high",
  "notes": "Make sure you're using the correct Python environment"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

