#!/usr/bin/env python3
"""
Simplified Backend Server - For Testing Frontend Connection
Does NOT require PyTorch (mock responses only)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI(
    title="URL Guardian Backend (MOCK)",
    description="Mock phishing detection backend for testing frontend",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UrlCheckRequest(BaseModel):
    url: str

class CheckResponse(BaseModel):
    probability: float
    label: str
    confidence: float = None

@app.get("/")
async def root():
    return {
        "message": "URL Guardian Backend (MOCK) is running",
        "version": "1.0.0",
        "note": "This is a mock server for testing frontend connection",
        "models_loaded": {
            "url": True,
            "html": True,
            "dom": True
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "device": "mock",
        "models": {
            "url": True,
            "html": True,
            "dom": True
        }
    }

@app.post("/api/check_url_fast", response_model=CheckResponse)
async def check_url(request: UrlCheckRequest):
    """Mock URL detection"""
    url = request.url.lower()
    
    # Simple mock logic
    if "phishing" in url or "verify" in url or "confirm" in url:
        return CheckResponse(
            probability=0.85,
            label="PHISHING",
            confidence=0.92
        )
    elif "suspicious" in url or "urgent" in url:
        return CheckResponse(
            probability=0.65,
            label="PHISHING",
            confidence=0.78
        )
    else:
        return CheckResponse(
            probability=0.15,
            label="BENIGN",
            confidence=0.88
        )

@app.post("/api/check_html", response_model=CheckResponse)
async def check_html(request: dict):
    """Mock HTML detection"""
    html = request.get("html", "").lower()
    
    if "verify account" in html or "confirm password" in html:
        return CheckResponse(
            probability=0.75,
            label="PHISHING",
            confidence=0.85
        )
    else:
        return CheckResponse(
            probability=0.25,
            label="BENIGN",
            confidence=0.90
        )

@app.post("/api/check_dom", response_model=CheckResponse)
async def check_dom(request: dict):
    """Mock DOM detection"""
    dom = request.get("dom", {})
    nodes_count = len(dom.get("nodes", []))
    
    if nodes_count > 50:
        return CheckResponse(
            probability=0.45,
            label="BENIGN",
            confidence=0.82
        )
    else:
        return CheckResponse(
            probability=0.35,
            label="BENIGN",
            confidence=0.88
        )

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 URL Guardian Backend (MOCK) - Testing Server")
    print("="*60)
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔗 Backend: http://localhost:8000")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
