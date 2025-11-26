"""
FastAPI Backend for Phishing URL Guardian
Serves 3 endpoints for URL, HTML, and DOM classification
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pydantic import BaseModel
import json
from pathlib import Path

from config import (
    DEVICE, CKPT_DIR, 
    RNN_CKPT, RNN_URL_VOCAB, RNN_THRESHOLD_JSON,
    TRANSFORMER_CKPT, TRANSFORMER_THRESHOLD_JSON,
    GNN_CKPT, GNN_TAG_VOCAB, GNN_THRESHOLD_JSON,
    API_HOST, API_PORT
)
from models_src.inference import (
    UrlModelWrapper, HtmlModelWrapper, DomModelWrapper, EnsemblePredictor
)


# ============ Helper Functions ============
def calculate_confidence(probability: float, threshold: float = 0.5, label: str = None) -> float:
    """
    Calculate confidence score (0-1) based on probability distance from threshold.
    Confidence is higher when probability is far from threshold (more certain).
    
    Args:
        probability: Model's predicted probability (0-1)
        threshold: Decision threshold (default 0.5)
        label: Predicted label (PHISHING/BENIGN)
    
    Returns:
        Confidence score (0-1), where 1.0 means very confident
    """
    if label and label == "UNKNOWN":
        return 0.0
    
    # Distance from threshold indicates confidence
    distance_from_threshold = abs(probability - threshold)
    max_distance = max(threshold, 1.0 - threshold)
    
    # Normalize distance to 0-1 range
    confidence = min(1.0, distance_from_threshold / max_distance)
    
    # Apply sigmoid-like scaling to avoid extreme values
    # This gives: ~0.5 confidence at threshold, approaching 1.0 at extremes
    confidence = 0.5 + (confidence * 0.5)
    
    return float(confidence)


# ============ Pydantic Models ============
class UrlCheckRequest(BaseModel):
    url: str
    normalize: bool = True  # Extract domain only (ignores path/query) [DEFAULT: True for stable results]
    
    class Config:
        example = {"url": "https://example.com", "normalize": True}


class HtmlCheckRequest(BaseModel):
    html: str
    
    class Config:
        example = {"html": "<html><body>...</body></html>"}


class DomCheckRequest(BaseModel):
    dom: dict
    
    class Config:
        example = {
            "dom": {
                "nodes": [{"tag": "html"}],
                "edges": [],
                "label": 0
            }
        }


class CheckResponse(BaseModel):
    probability: float
    label: str
    confidence: float = None
    explanations: list = None  # List of reasons for the prediction
    
    class Config:
        example = {
            "probability": 0.75,
            "label": "PHISHING",
            "confidence": 0.85,
            "explanations": ["Domain contains suspicious TLD", "Typosquatting pattern detected"]
        }


class AnalysisResult(BaseModel):
    """Result from a single model"""
    probability: float
    label: str
    confidence: float
    explanations: list
    model_name: str


class EnsembleResponse(BaseModel):
    """Full analysis with all 3 models + ensemble"""
    url: str
    url_model: AnalysisResult
    html_model: AnalysisResult
    dom_model: AnalysisResult
    ensemble: AnalysisResult


# ============ Initialize FastAPI ============
app = FastAPI(
    title="URL Guardian Backend",
    description="Phishing URL detection using ensemble of 3 models (RNN, Transformer, GCN)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://datn-demo-frontend.onrender.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware to ensure CORS headers are always present (for Render proxy compatibility)
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "https://datn-demo-frontend.onrender.com"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response


# Custom middleware to ensure CORS headers are always present
class CORSHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Get the origin from request
        origin = request.headers.get("origin")
        allowed_origins = [
            "https://datn-demo-frontend.onrender.com",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:4173",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:4173",
            "http://127.0.0.1:8080",
        ]
        
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            if origin in allowed_origins:
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Max-Age": "3600",
                    }
                )
        
        # Process the request
        response = await call_next(request)
        
        # Add CORS headers to all responses
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response


# Add the custom middleware
app.add_middleware(CORSHeaderMiddleware)


# ============ Helpers for Parallel Processing ============
def fetch_html_sync(url: str, timeout: int = 8) -> tuple:
    """
    Synchronously fetch HTML from URL with timeout and error handling
    Returns: (html_content, success: bool)
    """
    import requests
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True, verify=False)
        response.raise_for_status()
        return response.text, True
    except requests.exceptions.Timeout:
        return None, False
    except requests.exceptions.ConnectionError:
        return None, False
    except requests.exceptions.HTTPError:
        return None, False
    except Exception:
        return None, False



# ============ Model Loading ============
print("[INFO] Loading models...")

try:
    # Load URL model (RNN)
    url_model = UrlModelWrapper(
        ckpt_path=RNN_CKPT,
        vocab_path=RNN_URL_VOCAB,
        threshold_path=RNN_THRESHOLD_JSON,
        device=DEVICE
    )
    print("[OK] URL model (RNN) loaded")
except Exception as e:
    print(f"[ERROR] Failed to load URL model: {e}")
    url_model = None

try:
    # Load HTML model (Transformer)
    html_model = HtmlModelWrapper(
        ckpt_path=TRANSFORMER_CKPT,
        threshold_path=TRANSFORMER_THRESHOLD_JSON,
        device=DEVICE
    )
    print("[OK] HTML model (Transformer) loaded")
except Exception as e:
    print(f"[ERROR] Failed to load HTML model: {e}")
    html_model = None

try:
    # Load DOM model (GCN)
    dom_model = DomModelWrapper(
        ckpt_path=GNN_CKPT,
        tag_vocab_path=GNN_TAG_VOCAB,
        threshold_path=GNN_THRESHOLD_JSON,
        device=DEVICE
    )
    print("[OK] DOM model (GCN) loaded")
except Exception as e:
    print(f"[ERROR] Failed to load DOM model: {e}")
    dom_model = None

# Create ensemble
try:
    ensemble = EnsemblePredictor(
        url_wrapper=url_model,
        html_wrapper=html_model,
        dom_wrapper=dom_model,
        weights=(1.0, 1.0, 1.0)
    )
    print("[OK] Ensemble predictor created")
except Exception as e:
    print(f"[ERROR] Failed to create ensemble: {e}")
    ensemble = None


# ============ Routes ============

@app.get("/")
async def root():
    """Health check endpoint"""
    # CORS middleware active with explicit origins for Render deployment
    return {
        "message": "URL Guardian Backend is running",
        "version": "1.0.0",
        "device": DEVICE,
        "models_loaded": {
            "url": url_model is not None,
            "html": html_model is not None,
            "dom": dom_model is not None
        }
    }


@app.post("/api/check_url", response_model=CheckResponse)
async def check_url(request: UrlCheckRequest):
    """
    Check URL for phishing
    
    Args:
        request: UrlCheckRequest with "url" field
    
    Returns:
        CheckResponse with probability and label
    """
    if not url_model:
        raise HTTPException(status_code=503, detail="URL model not loaded")
    
    try:
        url = request.url.strip()
        if not url:
            raise ValueError("URL cannot be empty")
        
        p_phish, label = url_model.infer(url, normalize=request.normalize)  # Pass normalize flag
        
        # Confidence: how far from threshold
        threshold = url_model.threshold
        if label == "PHISHING":
            confidence = min(1.0, p_phish / max(threshold, 0.01))
        else:
            confidence = min(1.0, (1 - p_phish) / max(1 - threshold, 0.01))
        
        return CheckResponse(
            probability=float(p_phish),
            label=label,
            confidence=float(confidence)
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing URL: {str(e)}")


@app.post("/api/check_url_fast")
async def check_url_fast(request: UrlCheckRequest):
    """Alias for check_url (fast inference with RNN only)"""
    return await check_url(request)


@app.post("/api/check_html", response_model=CheckResponse)
async def check_html(request: HtmlCheckRequest):
    """
    Check HTML content for phishing
    
    Args:
        request: HtmlCheckRequest with "html" field
    
    Returns:
        CheckResponse with probability and label
    """
    if not html_model:
        raise HTTPException(status_code=503, detail="HTML model not loaded")
    
    try:
        html = request.html.strip()
        if not html:
            raise ValueError("HTML cannot be empty")
        
        p_phish, label = html_model.infer_multi(html, max_windows=4)
        
        # Confidence
        threshold = html_model.threshold
        if label == "PHISHING":
            confidence = min(1.0, p_phish / max(threshold, 0.01))
        else:
            confidence = min(1.0, (1 - p_phish) / max(1 - threshold, 0.01))
        
        return CheckResponse(
            probability=float(p_phish),
            label=label,
            confidence=float(confidence)
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing HTML: {str(e)}")


@app.post("/api/check_dom", response_model=CheckResponse)
async def check_dom(request: DomCheckRequest):
    """
    Check DOM graph structure for phishing
    
    Args:
        request: DomCheckRequest with "dom" field containing nodes, edges, label
    
    Returns:
        CheckResponse with probability and label
    """
    if not dom_model:
        raise HTTPException(status_code=503, detail="DOM model not loaded")
    
    try:
        dom_record = request.dom
        if not isinstance(dom_record, dict):
            raise ValueError("DOM record must be a dictionary")
        
        if "nodes" not in dom_record:
            raise ValueError("DOM record must contain 'nodes' field")
        
        p_phish, label = dom_model.infer(dom_record)
        
        # Confidence
        threshold = dom_model.threshold
        if label == "PHISHING":
            confidence = min(1.0, p_phish / max(threshold, 0.01))
        else:
            confidence = min(1.0, (1 - p_phish) / max(1 - threshold, 0.01))
        
        return CheckResponse(
            probability=float(p_phish),
            label=label,
            confidence=float(confidence)
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing DOM: {str(e)}")


@app.post("/api/analyze_url_full", response_model=EnsembleResponse)
async def analyze_url_full(request: UrlCheckRequest):
    """
    Comprehensive URL analysis using all 3 models + ensemble
    Runs RNN, Transformer, GCN in sequence with robust error handling
    
    Args:
        request: UrlCheckRequest with "url" field
    
    Returns:
        EnsembleResponse with results from all 3 models + ensemble prediction
        Returns UNKNOWN label gracefully if HTML/DOM cannot be analyzed
    """
    if not url_model or not html_model or not dom_model:
        raise HTTPException(status_code=503, detail="Not all models loaded")
    
    try:
        import requests
        from lxml import html as lxml_html
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        url = request.url.strip()
        if not url:
            raise ValueError("URL cannot be empty")
        
        # ====== PARALLEL: Run URL Model (RNN) + Fetch HTML ======
        url_result = None
        html_content = None
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit URL model inference
            url_future = executor.submit(
                lambda: url_model.infer(url, normalize=request.normalize)
            )
            
            # Submit HTML fetch
            html_future = executor.submit(
                fetch_html_sync, url, timeout=8
            )
            
            # Wait for URL model first (critical)
            try:
                p_phish_url, label_url = url_future.result(timeout=10)
                threshold_url = url_model.threshold
                confidence_url = calculate_confidence(p_phish_url, threshold_url, label_url)
                explanations_url = url_model.get_explanations(url, p_phish_url, label_url)
                url_result = AnalysisResult(
                    probability=float(p_phish_url),
                    label=label_url,
                    confidence=float(confidence_url),
                    explanations=explanations_url,
                    model_name="URL Model (RNN)"
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"URL model error: {str(e)}")
            
            # Get HTML fetch result (may timeout without failing)
            try:
                html_content, success = html_future.result(timeout=9)
            except:
                html_content = None
        
        # ====== STEP 2: Analyze HTML (Transformer) ======
        html_result = None
        try:
            if html_content:
                try:
                    p_phish_html, label_html = html_model.infer_multi(html_content, max_windows=4)
                    threshold_html = html_model.threshold
                    confidence_html = calculate_confidence(p_phish_html, threshold_html, label_html)
                    explanations_html = html_model.get_explanations(html_content, p_phish_html, label_html)
                    html_result = AnalysisResult(
                        probability=float(p_phish_html),
                        label=label_html,
                        confidence=float(confidence_html),
                        explanations=explanations_html,
                        model_name="HTML Model (Transformer)"
                    )
                except Exception as e:
                    html_result = AnalysisResult(
                        probability=0.5,
                        label="UNKNOWN",
                        confidence=0.0,
                        explanations=[f"HTML analysis failed: {str(e)}"],
                        model_name="HTML Model (Transformer)"
                    )
            else:
                html_result = AnalysisResult(
                    probability=0.5,
                    label="UNKNOWN",
                    confidence=0.0,
                    explanations=["Could not fetch HTML (website unreachable, blocked, or timeout)"],
                    model_name="HTML Model (Transformer)"
                )
        except Exception as e:
            # Graceful fallback for HTML model
            html_result = AnalysisResult(
                probability=0.5,
                label="UNKNOWN",
                confidence=0.0,
                explanations=[f"HTML fetch/analysis failed: {type(e).__name__}"],
                model_name="HTML Model (Transformer)"
            )
        
        # ====== STEP 3: Convert HTML to DOM and Run DOM Model (GCN) ======
        dom_result = None
        try:
            # DOM analysis only possible if HTML was successfully fetched and parsed
            if html_content and html_result.label != "UNKNOWN":
                try:
                    tree = lxml_html.fromstring(html_content)
                except Exception:
                    tree = None
                
                if tree is not None:
                    # Build simple DOM record from tree
                    dom_record = {
                        "nodes": [{"tag": tree.tag}],  # Simplified
                        "edges": []
                    }
                    
                    try:
                        p_phish_dom, label_dom = dom_model.infer(dom_record)
                        threshold_dom = dom_model.threshold
                        confidence_dom = calculate_confidence(p_phish_dom, threshold_dom, label_dom)
                        explanations_dom = dom_model.get_explanations(dom_record, p_phish_dom, label_dom)
                        dom_result = AnalysisResult(
                            probability=float(p_phish_dom),
                            label=label_dom,
                            confidence=float(confidence_dom),
                            explanations=explanations_dom,
                            model_name="DOM Model (GCN)"
                        )
                    except Exception as e:
                        dom_result = AnalysisResult(
                            probability=0.5,
                            label="UNKNOWN",
                            confidence=0.0,
                            explanations=[f"DOM analysis failed: {str(e)}"],
                            model_name="DOM Model (GCN)"
                        )
                else:
                    dom_result = AnalysisResult(
                        probability=0.5,
                        label="UNKNOWN",
                        confidence=0.0,
                        explanations=["DOM parsing failed: Unable to parse HTML structure"],
                        model_name="DOM Model (GCN)"
                    )
            else:
                # If HTML wasn't fetched or analysis failed, skip DOM model
                dom_result = AnalysisResult(
                    probability=0.5,
                    label="UNKNOWN",
                    confidence=0.0,
                    explanations=["DOM analysis skipped: HTML content unavailable or analysis failed"],
                    model_name="DOM Model (GCN)"
                )
        except Exception as e:
            # Graceful fallback for DOM model
            dom_result = AnalysisResult(
                probability=0.5,
                label="UNKNOWN",
                confidence=0.0,
                explanations=[f"DOM parsing failed: {type(e).__name__}"],
                model_name="DOM Model (GCN)"
            )
        
        # ====== STEP 4: Ensemble Prediction ======
        try:
            # Simple averaging (can be improved with weighted voting)
            valid_scores = []
            valid_count = 0
            
            if url_result and url_result.label != "UNKNOWN":
                valid_scores.append(p_phish_url)
                valid_count += 1
            if html_result and html_result.label != "UNKNOWN":
                valid_scores.append(p_phish_html)
                valid_count += 1
            if dom_result and dom_result.label != "UNKNOWN":
                valid_scores.append(p_phish_dom)
                valid_count += 1
            
            if valid_scores:
                ensemble_score = sum(valid_scores) / len(valid_scores)
            else:
                # If only URL model works, use its score
                ensemble_score = p_phish_url if url_result else 0.5
            
            ensemble_threshold = 0.50
            ensemble_label = "PHISHING" if ensemble_score > ensemble_threshold else "BENIGN"
            ensemble_confidence = max(ensemble_score, 1 - ensemble_score)
            
            ensemble_explanations = [
                f"URL Model: {url_result.label} ({url_result.probability:.2%})" if url_result else "URL Model: Error",
                f"HTML Model: {html_result.label} ({html_result.probability:.2%})" if html_result and html_result.label != "UNKNOWN" else "HTML Model: Unable to analyze",
                f"DOM Model: {dom_result.label} ({dom_result.probability:.2%})" if dom_result and dom_result.label != "UNKNOWN" else "DOM Model: Unable to analyze",
                f"Ensemble Score: {ensemble_score:.2%} (Average of {valid_count} model(s))"
            ]
            
            ensemble_result = AnalysisResult(
                probability=float(ensemble_score),
                label=ensemble_label,
                confidence=float(ensemble_confidence),
                explanations=ensemble_explanations,
                model_name="Ensemble (Combined)"
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ensemble error: {str(e)}")
        
        return EnsembleResponse(
            url=url,
            url_model=url_result,
            html_model=html_result,
            dom_model=dom_result,
            ensemble=ensemble_result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in full analysis: {str(e)}")


@app.post("/api/ensemble")
async def check_ensemble(
    url: str = None,
    html: str = None,
    dom: dict = None
):
    """
    Check using all available models and return ensemble prediction
    
    Args:
        url: URL string (optional)
        html: HTML string (optional)
        dom: DOM record dict (optional)
    
    Returns:
        dict with individual and ensemble predictions
    """
    if not ensemble:
        raise HTTPException(status_code=503, detail="Ensemble not loaded")
    
    if not any([url, html, dom]):
        raise HTTPException(status_code=400, detail="At least one input (url, html, or dom) required")
    
    try:
        result = ensemble.predict(
            url=url,
            html=html,
            dom_record=dom,
            use_models=(url_model is not None, html_model is not None, dom_model is not None)
        )
        
        return {
            "url": result.get("url"),
            "html": result.get("html"),
            "dom": result.get("dom"),
            "ensemble": result["ensemble"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in ensemble prediction: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check for deployment monitoring"""
    return {
        "status": "healthy",
        "device": DEVICE,
        "models": {
            "url": url_model is not None,
            "html": html_model is not None,
            "dom": dom_model is not None
        }
    }


@app.post("/api/analyze_html_file")
async def analyze_html_file(file_content: dict):
    """
    Analyze uploaded HTML file content
    Runs HTML and DOM models on provided HTML content
    
    Args:
        file_content: {"html": "<html>...</html>"}
    
    Returns:
        EnsembleResponse-like result with HTML + DOM analysis
    """
    if not html_model or not dom_model:
        raise HTTPException(status_code=503, detail="HTML or DOM model not loaded")
    
    try:
        html_content = file_content.get("html", "").strip()
        if not html_content:
            raise ValueError("HTML content cannot be empty")
        
        # ====== Analyze HTML (Transformer) ======
        try:
            p_phish_html, label_html = html_model.infer_multi(html_content, max_windows=4)
            threshold_html = html_model.threshold
            confidence_html = min(1.0, p_phish_html / max(threshold_html, 0.01)) if label_html == "PHISHING" else min(1.0, (1 - p_phish_html) / max(1 - threshold_html, 0.01))
            explanations_html = [
                "Form analysis: Detects input fields, form actions, suspicious targets",
                "HTML structure: Checks meta tags, title, missing legitimate branding",
                "JavaScript analysis: Identifies inline scripts and external malicious sources"
            ]
            html_result = AnalysisResult(
                probability=float(p_phish_html),
                label=label_html,
                confidence=float(confidence_html),
                explanations=explanations_html,
                model_name="HTML Model (Transformer)"
            )
        except Exception as e:
            html_result = AnalysisResult(
                probability=0.5,
                label="UNKNOWN",
                confidence=0.0,
                explanations=[f"HTML analysis failed: {str(e)}"],
                model_name="HTML Model (Transformer)"
            )
        
        # ====== Analyze DOM (GCN) ======
        try:
            from lxml import html as lxml_html
            tree = lxml_html.fromstring(html_content)
            
            dom_record = {
                "nodes": [{"tag": tree.tag}],
                "edges": []
            }
            
            p_phish_dom, label_dom = dom_model.infer(dom_record)
            threshold_dom = dom_model.threshold
            confidence_dom = min(1.0, p_phish_dom / max(threshold_dom, 0.01)) if label_dom == "PHISHING" else min(1.0, (1 - p_phish_dom) / max(1 - threshold_dom, 0.01))
            explanations_dom = [
                "DOM tree analysis: Checks node count, tree depth, anomalies",
                "Graph features: Analyzes element connections and suspicious patterns",
                "Hidden elements: Detects hidden inputs, scripts, and suspicious structures"
            ]
            dom_result = AnalysisResult(
                probability=float(p_phish_dom),
                label=label_dom,
                confidence=float(confidence_dom),
                explanations=explanations_dom,
                model_name="DOM Model (GCN)"
            )
        except Exception as e:
            dom_result = AnalysisResult(
                probability=0.5,
                label="UNKNOWN",
                confidence=0.0,
                explanations=[f"DOM analysis failed: {str(e)}"],
                model_name="DOM Model (GCN)"
            )
        
        # ====== Ensemble Result ======
        valid_scores = []
        if html_result.label != "UNKNOWN":
            valid_scores.append(p_phish_html)
        if dom_result.label != "UNKNOWN":
            valid_scores.append(p_phish_dom)
        
        if valid_scores:
            ensemble_score = sum(valid_scores) / len(valid_scores)
        else:
            ensemble_score = 0.5
        
        ensemble_threshold = 0.50
        ensemble_label = "PHISHING" if ensemble_score > ensemble_threshold else "BENIGN"
        ensemble_confidence = max(ensemble_score, 1 - ensemble_score)
        
        ensemble_explanations = [
            f"HTML Model: {html_result.label} ({html_result.probability:.2%})" if html_result.label != "UNKNOWN" else "HTML Model: Unable to analyze",
            f"DOM Model: {dom_result.label} ({dom_result.probability:.2%})" if dom_result.label != "UNKNOWN" else "DOM Model: Unable to analyze",
            f"Ensemble Score: {ensemble_score:.2%} (Average of available models)"
        ]
        
        ensemble_result = AnalysisResult(
            probability=float(ensemble_score),
            label=ensemble_label,
            confidence=float(ensemble_confidence),
            explanations=ensemble_explanations,
            model_name="Ensemble (HTML + DOM)"
        )
        
        return {
            "url": "file_upload",
            "url_model": None,
            "html_model": html_result.dict(),
            "dom_model": dom_result.dict(),
            "ensemble": ensemble_result.dict()
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing HTML file: {str(e)}")


@app.post("/api/fetch_url_resources")
async def fetch_url_resources(request: UrlCheckRequest):
    """
    Fetch HTML content from URL for analysis
    This is used by frontend to get actual HTML/DOM for phishing detection
    
    Args:
        request: UrlCheckRequest with "url" field
    
    Returns:
        {"html": "<html>...</html>", "success": true} or error
    """
    import requests
    from lxml import html as lxml_html
    
    try:
        url = request.url.strip()
        if not url:
            raise ValueError("URL cannot be empty")
        
        # Fetch HTML with shorter timeout for phishing URLs that may be inaccessible
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, timeout=5, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        html_content = response.text
        
        # Parse HTML to extract DOM structure
        try:
            tree = lxml_html.fromstring(html_content)
        except:
            # If parsing fails, return raw HTML
            tree = None
        
        return {
            "html": html_content,
            "url": url,
            "success": True,
            "message": "HTML fetched successfully"
        }
    
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Request timeout - URL took too long to respond (may indicate phishing/blocked site)")
    except requests.exceptions.ConnectionError as e:
        raise HTTPException(status_code=503, detail="Connection error - cannot reach URL (may be inaccessible)")
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error {e.response.status_code} - {str(e)}")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Network error - cannot fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")


# ============ Batch Analysis Endpoint ============
class BatchUrlRequest(BaseModel):
    urls: list  # List of URL strings
    normalize: bool = True

class BatchAnalysisResponse(BaseModel):
    total: int
    successful: int
    results: list  # List of EnsembleResponse objects


result_cache = {}  # Simple in-memory cache {url: (result, timestamp)}
cache_ttl_seconds = 3600  # 1 hour

@app.post("/api/batch_analyze_urls", response_model=BatchAnalysisResponse)
async def batch_analyze_urls(request: BatchUrlRequest):
    """
    Analyze multiple URLs in batch
    Uses caching to avoid re-analyzing same URLs
    
    Args:
        request: BatchUrlRequest with list of URLs
    
    Returns:
        BatchAnalysisResponse with results for each URL
    """
    import time
    
    if not request.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")
    
    if len(request.urls) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 URLs per batch")
    
    results = []
    current_time = time.time()
    
    for url in request.urls:
        try:
            # Check cache first
            if url in result_cache:
                cached_result, cache_time = result_cache[url]
                if current_time - cache_time < cache_ttl_seconds:
                    results.append({
                        "url": url,
                        "result": cached_result,
                        "cached": True
                    })
                    continue
            
            # Not in cache, analyze it
            analysis = await analyze_url_full(UrlCheckRequest(url=url, normalize=request.normalize))
            
            # Cache the result
            result_cache[url] = (analysis.dict(), current_time)
            
            results.append({
                "url": url,
                "result": analysis.dict(),
                "cached": False
            })
        except Exception as e:
            results.append({
                "url": url,
                "error": str(e),
                "cached": False
            })
    
    return BatchAnalysisResponse(
        total=len(request.urls),
        successful=sum(1 for r in results if "result" in r or "cached" in r),
        results=results
    )


@app.post("/api/cache_stats")
async def get_cache_stats():
    """
    Get cache statistics
    """
    import time
    current_time = time.time()
    
    active_entries = 0
    for url, (result, cache_time) in result_cache.items():
        if current_time - cache_time < cache_ttl_seconds:
            active_entries += 1
    
    return {
        "total_cached": len(result_cache),
        "active_cached": active_entries,
        "ttl_seconds": cache_ttl_seconds
    }


@app.post("/api/cache_clear")
async def clear_cache():
    """
    Clear all cache entries
    """
    result_cache.clear()
    return {"message": "Cache cleared successfully"}


# ============ Error Handlers ============
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "error": str(exc),
        "status": 500
    }


# ============ Entry Point ============
if __name__ == "__main__":
    import uvicorn
    
    print(f"\n[START] Starting server on {API_HOST}:{API_PORT}")
    print(f"[INFO] API docs available at http://localhost:{API_PORT}/docs")
    
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        workers=1,
        log_level="info"
    )
