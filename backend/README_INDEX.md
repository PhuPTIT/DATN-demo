# 📚 Backend Implementation - Quick Reference

## 🚀 START HERE

### Quick Start (Copy-Paste Ready)

```bash
# 1. Go to backend
cd backend

# 2. Install dependencies (takes ~2 minutes)
pip install -r requirements.txt

# 3. Run the server
python main.py

# Expected output:
# ✅ URL model (RNN) loaded
# ✅ HTML model (Transformer) loaded  
# ✅ DOM model (GCN) loaded
# ✅ Ensemble predictor created
# 🌐 Starting server on 0.0.0.0:8000
```

### Test Endpoints

```bash
# In another terminal:

# Test URL detection
curl -X POST http://localhost:8000/api/check_url_fast \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Test HTML detection
curl -X POST http://localhost:8000/api/check_html \
  -H "Content-Type: application/json" \
  -d '{"html": "<html><body></body></html>"}'

# Test DOM detection
curl -X POST http://localhost:8000/api/check_dom \
  -H "Content-Type: application/json" \
  -d '{"dom": {"nodes": [{"tag": "html"}], "edges": [], "label": 0}}'
```

### View Interactive Docs

Open browser: **http://localhost:8000/docs**

---

## 📂 File Guide

### Essential Files

| File | Purpose | Lines |
|------|---------|-------|
| **main.py** | FastAPI app + endpoints | 340 |
| **config.py** | Paths & configuration | 60 |
| **requirements.txt** | Python dependencies | 15 |

### Model Code

| File | Purpose | Lines |
|------|---------|-------|
| **models_src/architectures.py** | GRUUrl, Transformer, GCN | 250 |
| **models_src/preprocessing.py** | URL/HTML/DOM encoding | 500 |
| **models_src/inference.py** | Model wrappers | 330 |

### Documentation

| File | Purpose | When to Read |
|------|---------|-------------|
| **README.md** | User guide & API docs | Before running |
| **IMPLEMENTATION.md** | Technical details | For integration |
| **ARCHITECTURE.md** | System design & diagrams | For understanding |

---

## 🎯 API Endpoints

### 1. Check URL (Fast)
```
POST /api/check_url_fast
Request:  {"url": "https://example.com"}
Response: {"probability": 0.25, "label": "BENIGN", "confidence": 0.92}
Speed:    ~20-50ms
```

### 2. Check HTML
```
POST /api/check_html
Request:  {"html": "<html>...</html>"}
Response: {"probability": 0.62, "label": "PHISHING", "confidence": 0.78}
Speed:    ~100-500ms
```

### 3. Check DOM
```
POST /api/check_dom
Request:  {"dom": {"nodes": [...], "edges": [...], "label": 0}}
Response: {"probability": 0.58, "label": "PHISHING", "confidence": 0.72}
Speed:    ~100-1000ms
```

---

## 🔍 Understanding the Code

### Model Architecture

```
RNN (URL):
  URL string (256 chars)
  ↓ encode to char indices
  ↓ GRU embedding + bidirectional
  ↓ classify → probability

Transformer (HTML):
  HTML content (2048 bytes × 4 windows)
  ↓ UTF-8 byte encoding
  ↓ Multi-window Transformer
  ↓ Average logits → probability

GCN (DOM):
  DOM tree (2048 nodes max)
  ↓ Extract node features (70-dim)
  ↓ Build sparse adjacency
  ↓ GCN forward pass
  ↓ Graph pooling → probability
```

### Data Flow

```
User Request
  ↓
Validation (Pydantic)
  ↓
Preprocessing
  ↓
Model Inference
  ↓
Apply Threshold
  ↓
Return JSON Response
```

---

## ⚙️ Configuration

### Change Device (GPU/CPU)

In `config.py`:
```python
DEVICE = "cuda"  # For GPU
DEVICE = "cpu"   # For CPU
```

### Change API Port

In `config.py`:
```python
API_PORT = 8000  # or any other port
```

### Change Model Hyperparameters

In `config.py`:
```python
RNN_CONFIG["hidden_dim"] = 256  # Increase from 128
TRANSFORMER_CONFIG["n_layers"] = 8  # Increase from 4
GNN_CONFIG["hidden_dim"] = 256  # Increase from 128
```

---

## 🛠️ Common Tasks

### Run Server in Development Mode
```bash
python main.py
# Auto-reloads on code changes
```

### Run with Uvicorn Directly
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Run on Different Port
```bash
# In config.py, change:
API_PORT = 9000
# Then run:
python main.py
```

### Test All Endpoints
```bash
# Use the Swagger UI at http://localhost:8000/docs
# Or use the curl commands above
```

### Check Server Status
```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy", "device": "cuda", "models": {...}}
```

---

## 🐛 Debug Checklist

- [ ] CKPT folder exists at `../CKPT`
- [ ] All checkpoint files present (`*.pt`, `*.json`)
- [ ] Python 3.8+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] No port conflicts (default 8000)
- [ ] GPU available if using CUDA

---

## 📊 Model Details

### RNN Model
- **Vocab**: 87 characters (a-z, 0-9, special chars)
- **Input**: Up to 256 characters
- **Threshold**: 0.5
- **File**: `rnn_best_ema.pt`

### Transformer Model
- **Vocab**: 259 tokens (0-255 bytes + special)
- **Input**: Up to 2048 tokens × 4 windows
- **Threshold**: 0.34
- **File**: `transformer_byte_best.pt`

### GCN Model
- **Vocab**: 64 HTML tags
- **Features**: 70 per node (tags + attributes)
- **Input**: Up to 2048 nodes
- **Threshold**: 0.54
- **File**: `gnn_best.pt`

---

## 🚢 Deployment

### Docker
```bash
# Build
docker build -t url-guardian-backend .

# Run
docker run -p 8000:8000 url-guardian-backend
```

### Cloud (AWS ECS, GCP Cloud Run, etc.)
1. Create Docker image
2. Push to registry
3. Deploy as container
4. Set environment variables if needed

---

## 🔗 Frontend Integration

### JavaScript/TypeScript
```typescript
const checkUrl = async (url: string) => {
  const response = await fetch('http://localhost:8000/api/check_url_fast', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  return response.json();
};

const result = await checkUrl('https://example.com');
console.log(result); // {probability: 0.25, label: "BENIGN", ...}
```

### Python
```python
import requests

result = requests.post(
  'http://localhost:8000/api/check_url_fast',
  json={'url': 'https://example.com'}
).json()
print(result)  # {'probability': 0.25, 'label': 'BENIGN', ...}
```

---

## 📈 Performance Tips

- **Faster**: Use `check_url_fast` (RNN only)
- **More Accurate**: Use `check_html` with multi-window
- **Comprehensive**: Use ensemble endpoint
- **Production**: Deploy on GPU for best speed

---

## ❓ FAQ

**Q: How long does it take to load models?**
A: ~5-10 seconds on first startup (cached after that)

**Q: Can I run on CPU?**
A: Yes, set `DEVICE = "cpu"` in config.py

**Q: What if GPU runs out of memory?**
A: Reduce batch size or use CPU

**Q: Can I use different thresholds?**
A: Yes, edit the threshold JSON files in CKPT/

**Q: How do I add a new model?**
A: Add architecture, preprocessing, wrapper, and endpoint

---

## 📚 Documentation Map

```
If you want to...              Read this file
─────────────────────────────────────────────────
Get started quickly            README.md
Understand the code            IMPLEMENTATION.md
See system architecture         ARCHITECTURE.md
Understand this index          README_INDEX.md (this file)
See all details                BACKEND_SUMMARY.txt
Check completion               BACKEND_CHECKLIST.md
```

---

## ✨ What's Implemented

✅ 3 Deep Learning Models (RNN, Transformer, GCN)
✅ 3 API Endpoints (URL, HTML, DOM)
✅ Multi-window inference (robust HTML)
✅ Ensemble prediction
✅ Automatic GPU detection
✅ CORS support
✅ Interactive API docs (Swagger UI)
✅ Health checks
✅ Error handling
✅ Comprehensive documentation

---

## 🎓 Learning Path

1. **Run it**: `python main.py` → See it work
2. **Test it**: Use Swagger UI → See endpoints
3. **Read README.md** → Understand usage
4. **Read IMPLEMENTATION.md** → Understand code
5. **Read ARCHITECTURE.md** → Understand design
6. **Modify it**: Change configs → Experiment

---

## 🚀 Next Steps

1. ✅ Run backend: `python main.py`
2. ✅ Test endpoints via Swagger UI
3. 🔜 Connect frontend to API
4. 🔜 Deploy to production
5. 🔜 Monitor performance

---

## 💡 Pro Tips

- Use Swagger UI (`/docs`) to test all endpoints
- Start with simple URL checks, then add HTML/DOM
- Monitor latency to optimize model selection
- Cache results for repeated URLs
- Batch requests for higher throughput

---

## 🆘 Need Help?

1. Check **README.md** for quick solutions
2. Check **ARCHITECTURE.md** for system design
3. Check **IMPLEMENTATION.md** for technical details
4. Review error messages in terminal
5. Verify CKPT files are present

---

**You're ready! Run `python main.py` to start. 🚀**
