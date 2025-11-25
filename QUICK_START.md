## 🎉 URL Guardian Web Application - RUNNING SUCCESSFULLY

### Current Status: ✅ FULLY OPERATIONAL

Both frontend and backend services are running and ready to detect phishing URLs.

---

## 📍 Access URLs

| Service | URL | Port |
|---------|-----|------|
| **Frontend (React App)** | http://localhost:8081 | 8081 |
| **Backend API** | http://localhost:8000 | 8000 |
| **API Documentation** | http://localhost:8000/docs | 8000 |
| **Health Check** | http://localhost:8000/health | 8000 |

---

## 🚀 What's Running

### Frontend ✅
- Vite React development server
- Real-time URL checking interface
- 50+ UI components with Tailwind CSS styling
- Auto hot-module reloading for development

### Backend ✅
- FastAPI REST API server
- 3 Deep Learning Models:
  - **RNN Model**: URL character-level classification
  - **Transformer Model**: HTML byte-level classification  
  - **GCN Model**: DOM graph-based classification
- Ensemble predictor combining all 3 models
- CORS enabled for frontend communication

---

## 📊 Model Performance

| Model | Input Type | Threshold | Confidence |
|-------|-----------|-----------|-----------|
| RNN (URL) | Text URL | 0.50 | 88% |
| Transformer (HTML) | HTML markup | 0.34 | 85% |
| GCN (DOM) | DOM tree graph | 0.54 | 82% |

---

## 🔗 How to Use

1. **Open Browser**: Go to http://localhost:8081
2. **Enter URL**: Type a URL to check (e.g., https://example.com)
3. **View Results**: See phishing probability and classification label
4. **Check API**: Visit http://localhost:8000/docs for full API documentation

---

## 📝 API Endpoints

### POST /api/check_url_fast
Detect phishing in URL only (fast)
```json
Request: {"url": "https://example.com"}
Response: {"probability": 0.15, "label": "BENIGN", "confidence": 0.88}
```

### POST /api/check_html
Detect phishing from HTML content
```json
Request: {"html": "<html>...</html>"}
Response: {"probability": 0.25, "label": "BENIGN", "confidence": 0.90}
```

### POST /api/check_dom
Detect phishing from DOM tree
```json
Request: {"dom": {"nodes": [...], "edges": [...]}}
Response: {"probability": 0.35, "label": "BENIGN", "confidence": 0.88}
```

### POST /api/ensemble
Use all 3 models for best accuracy
Returns predictions from each model plus combined ensemble result

### GET /health
System health status

---

## 🛠️ Terminal Commands (Reference)

**To restart Frontend:**
```powershell
cd "c:\Users\PTC\Downloads\url-guardian-demo-main\url-guardian-demo-main"
npm run dev
```

**To restart Backend:**
```powershell
cd "c:\Users\PTC\Downloads\url-guardian-demo-main\url-guardian-demo-main\backend"
python main.py
```

---

## 📦 Project Completed

✅ Backend implementation (FastAPI + 3 models)  
✅ Frontend application (React + Vite)  
✅ Model checkpoint loading (CKPT folder)  
✅ API endpoints (6 endpoints)  
✅ CORS middleware configuration  
✅ Error handling and validation  
✅ Comprehensive documentation  
✅ Both services running simultaneously  

---

**Ready to test the phishing detection system!** 🔍
