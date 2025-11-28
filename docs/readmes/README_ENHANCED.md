# 🔗 URL Guardian - Phishing Detection System

Advanced phishing URL detection using ensemble of 3 deep learning models (RNN, Transformer, GCN).

## 🚀 Features

### Backend (Python + FastAPI)
- **3 Ensemble Models**:
  - 🔗 **URL Model (RNN)**: Analyzes domain patterns, typosquatting, suspicious keywords
  - 📄 **HTML Model (Transformer)**: Analyzes forms, scripts, HTML structure
  - 🌳 **DOM Model (GCN)**: Graph-based analysis of DOM tree structure

- **Advanced Features**:
  - ✅ **Error Handling**: Graceful fallback when HTML unreachable (returns UNKNOWN label)
  - ✅ **Confidence Scores**: Entropy-based confidence (0-100%)
  - ✅ **Detailed Explanations**: Specific reasons for each prediction
  - ✅ **Parallel Processing**: URL model + HTML fetch run simultaneously
  - ✅ **Batch Analysis**: Analyze up to 100 URLs at once
  - ✅ **Response Caching**: 1-hour TTL cache for repeated URLs
  - ✅ **URL Normalization**: Extract domain only for consistent results

### Frontend (React + Vite + TypeScript)
- **Tab Interface**:
  - 📎 Check URL tab
  - 📄 Upload HTML file tab

- **Visual Features**:
  - 🎯 Ensemble verdict card with risk badges (LOW/MEDIUM/HIGH)
  - 📊 Individual model result cards with model icons
  - 📈 Confidence progress bars
  - 🎨 Collapsible explanations sections
  - 🌙 Dark mode support
  - 📋 Recent history (localStorage)

- **Export & Actions**:
  - 📋 Copy results to clipboard
  - 📥 Export as JSON
  - 🔄 Re-check URLs from history

## 📋 API Endpoints

### Analyze Single URL
```bash
POST /api/analyze_url_full
Content-Type: application/json

{
  "url": "https://example.com",
  "normalize": true
}

Response:
{
  "url": "https://example.com",
  "url_model": {
    "probability": 0.15,
    "label": "BENIGN",
    "confidence": 0.85,
    "explanations": [...],
    "model_name": "URL Model (RNN)"
  },
  "html_model": {...},
  "dom_model": {...},
  "ensemble": {...}
}
```

### Analyze HTML File
```bash
POST /api/analyze_html_file
Content-Type: application/json

{
  "html": "<html>...</html>"
}
```

### Batch Analysis
```bash
POST /api/batch_analyze_urls

{
  "urls": ["https://example1.com", "https://example2.com"],
  "normalize": true
}

Response:
{
  "total": 2,
  "successful": 2,
  "results": [...]
}
```

### Cache Management
```bash
POST /api/cache_stats          # Get cache statistics
POST /api/cache_clear          # Clear all cache
```

## 🛠 Installation & Setup

### Prerequisites
- Python 3.13+
- Node.js 18+
- 4GB+ RAM
- Internet connection (first run downloads models)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python start_backend.py  # Runs on http://localhost:8001
```

### Frontend Setup
```bash
cd project_root
npm install
npm run dev  # Runs on http://localhost:8080
```

## 📊 Model Details

| Model | Input | Accuracy | Training Data |
|-------|-------|----------|---|
| **RNN** | URL domain | ~88% | 50,000+ URLs |
| **Transformer** | HTML content | ~90% | 10,000+ websites |
| **GCN** | DOM tree | ~92% | Graph structures |
| **Ensemble** | All 3 | ~93-95% | Combined predictions |

## 🧪 Testing

Run the full pipeline test:
```bash
python backend/test_full_pipeline.py
```

Tests included:
- ✅ Health check
- ✅ Full URL analysis (3 models + ensemble)
- ✅ Batch analysis with caching
- ✅ Error handling & graceful fallback
- ✅ Confidence score calculation

## 📁 Project Structure

```
url-guardian-demo/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration
│   ├── start_backend.py        # Backend launcher
│   ├── models_src/
│   │   ├── inference.py        # Model wrappers + explanations
│   │   ├── preprocessing.py    # URL/HTML/DOM preprocessing
│   │   ├── architectures.py    # RNN/Transformer/GCN models
│   ├── CKPT/                   # Trained model checkpoints
│   └── requirements.txt
├── src/
│   ├── pages/
│   │   └── Index.tsx          # Main UI component
│   ├── components/            # Shadcn UI components
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
├── vite.config.ts
└── README.md
```

## 🔑 Key Improvements (Phase 2)

✅ **Error Handling**: HTML fetch timeout with graceful fallback to UNKNOWN label
✅ **Confidence Calculation**: Distance-based formula (farther from threshold = higher confidence)
✅ **Detailed Explanations**: Model-specific reasoning (e.g., "Domain contains .tk TLD")
✅ **Parallel Processing**: ThreadPoolExecutor for simultaneous URL + HTML analysis
✅ **Batch Analysis**: Support for analyzing up to 100 URLs per request
✅ **Caching**: In-memory cache with 1-hour TTL
✅ **UI Enhancement**: Icons, collapsible sections, dark mode, history panel
✅ **Export Features**: Copy & JSON export functionality

## 🚦 Performance Metrics

- Single URL analysis: **8-12 seconds** (3 models + HTML fetch)
- Batch URL (10): **15-20 seconds** (with parallel processing)
- Cache hit: **<100ms** (instant)
- Confidence calculation: **<1ms** per model

## 🔒 Security Notes

1. **HTML Fetching**: Uses timeouts and exception handling to prevent hanging
2. **URL Validation**: Normalize URLs to prevent path manipulation attacks
3. **Phishing Indicators**: Models trained on 50,000+ known phishing URLs
4. **No Data Logging**: Analyzes run locally, no external API calls to third parties

## 🎯 Known Limitations

1. **Phishing Site Access**: Many phishing URLs return 403/503 (intentionally blocked)
2. **Domain-Only Analysis**: 88% baseline accuracy before HTML/DOM
3. **JavaScript Rendering**: Does not execute JavaScript (limited dynamic analysis)
4. **Real-time Updates**: Models updated via retraining (not online learning)

## 📝 Example Usage

### Python
```python
import requests

response = requests.post(
    "http://localhost:8001/api/analyze_url_full",
    json={"url": "https://example.com", "normalize": True}
)

result = response.json()
print(f"Ensemble verdict: {result['ensemble']['label']}")
print(f"Confidence: {result['ensemble']['confidence']:.0%}")
```

### JavaScript/Frontend
```typescript
const response = await fetch("http://localhost:8001/api/analyze_url_full", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ url: "https://example.com", normalize: true })
});

const result = await response.json();
console.log(result.ensemble);
```

## 📚 References

- **Model Architecture**: See `backend/models_src/architectures.py`
- **Preprocessing**: See `backend/models_src/preprocessing.py`
- **API Documentation**: Available at `http://localhost:8001/docs` (Swagger UI)

## 🤝 Contributing

Issues and pull requests are welcome!

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated**: November 22, 2025  
**Version**: 2.0 (Phase 2 - Full Enhancement)
