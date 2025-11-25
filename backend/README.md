# 🛡️ URL Guardian Backend

Phishing URL detection backend using ensemble of 3 deep learning models (RNN, Transformer, GCN).

## 📋 Architecture

### 3 Models:

1. **RNN (URL Model)**
   - Architecture: GRU with embeddings
   - Input: URL string (encoded to character indices)
   - Max length: 256 characters
   - Output: Phishing probability
   - Speed: ⚡ Fast (~10-50ms)

2. **Transformer (HTML Model)**
   - Architecture: Byte-level Transformer encoder
   - Input: HTML content (UTF-8 bytes)
   - Max length: 2048 tokens
   - Multi-window inference: 4 windows for robustness
   - Output: Phishing probability
   - Speed: 🚀 Medium (~100-500ms)

3. **GCN (DOM Model)**
   - Architecture: Graph Convolutional Network
   - Input: DOM tree as graph (nodes + edges)
   - Node features: HTML tags + attributes (64 tag types + 6 extra features)
   - Max nodes: 2048
   - Output: Phishing probability
   - Speed: 🚀 Slow (~200-1000ms)

### Ensemble Strategy:
- Weighted averaging of 3 models (default: equal weights)
- Each model votes independently
- Final decision: averaged probability > 0.5 → PHISHING

## 📁 Directory Structure

```
backend/
├── main.py                    # FastAPI app + 3 endpoints
├── config.py                  # Configuration & paths
├── requirements.txt           # Python dependencies
├── models_src/
│   ├── __init__.py
│   ├── architectures.py       # PyTorch model definitions
│   ├── preprocessing.py       # Input preprocessing utilities
│   └── inference.py           # Model loading & inference
├── CKPT/                      # (symlinked from ../CKPT)
│   ├── rnn_best_ema.pt
│   ├── rnn_url_vocab.json
│   ├── rnn_best_threshold.json
│   ├── transformer_byte_best.pt
│   ├── transformer_best_threshold.json
│   ├── gnn_best.pt
│   ├── gnn_tag_vocab.json
│   └── gnn_best_threshold.json
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Test Endpoints

#### Health Check
```bash
curl http://localhost:8000/
```

#### Check URL
```bash
curl -X POST http://localhost:8000/api/check_url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Response:
```json
{
  "probability": 0.25,
  "label": "BENIGN",
  "confidence": 0.92
}
```

#### Check HTML
```bash
curl -X POST http://localhost:8000/api/check_html \
  -H "Content-Type: application/json" \
  -d '{"html": "<html><body>...</body></html>"}'
```

#### Check DOM
```bash
curl -X POST http://localhost:8000/api/check_dom \
  -H "Content-Type: application/json" \
  -d '{"dom": {"nodes": [{"tag": "html"}], "edges": [], "label": 0}}'
```

#### Ensemble Prediction
```bash
curl -X POST http://localhost:8000/api/ensemble?url=https://example.com&html=<html>...</html>
```

### 4. Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### POST `/api/check_url` / `/api/check_url_fast`
Fast URL-only phishing detection

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "probability": 0.75,
  "label": "PHISHING",
  "confidence": 0.85
}
```

---

### POST `/api/check_html`
HTML content phishing detection (multi-window)

**Request:**
```json
{
  "html": "<html><body>Suspicious page</body></html>"
}
```

**Response:**
```json
{
  "probability": 0.62,
  "label": "PHISHING",
  "confidence": 0.78
}
```

---

### POST `/api/check_dom`
DOM graph structure phishing detection

**Request:**
```json
{
  "dom": {
    "nodes": [
      {"tag": "html"},
      {"tag": "body"},
      {"tag": "a", "attrs": {"href": "http://suspicious.com"}}
    ],
    "edges": [[0, 1], [1, 2]],
    "label": 0
  }
}
```

**Response:**
```json
{
  "probability": 0.58,
  "label": "PHISHING",
  "confidence": 0.72
}
```

---

### POST `/api/ensemble`
Ensemble prediction using all 3 models

**Request (form data or query params):**
```
url=https://example.com
html=<html>...</html>
dom={"nodes": [...], "edges": [...]}
```

**Response:**
```json
{
  "url": {
    "prob": 0.25,
    "label": "BENIGN"
  },
  "html": {
    "prob": 0.62,
    "label": "PHISHING"
  },
  "dom": {
    "prob": 0.58,
    "label": "PHISHING"
  },
  "ensemble": {
    "prob": 0.48,
    "label": "BENIGN"
  }
}
```

---

### GET `/health`
Health check for monitoring

**Response:**
```json
{
  "status": "healthy",
  "device": "cuda",
  "models": {
    "url": true,
    "html": true,
    "dom": true
  }
}
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Device
DEVICE = "cuda"  # or "cpu"

# Paths (auto-detected)
CKPT_DIR = Path(__file__).parent.parent / "CKPT"

# Model hyperparameters
RNN_CONFIG = {
    "emb_dim": 64,
    "hidden_dim": 128,
    "max_len": 256,
}

TRANSFORMER_CONFIG = {
    "d_model": 192,
    "n_head": 6,
    "n_layers": 4,
    "max_len": 2048,
}

GNN_CONFIG = {
    "hidden_dim": 128,
    "max_nodes": 2048,
}

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
```

## 📊 Model Details

### URL Model (RNN)
- **Input**: URL string → UTF-8 character indices (87 characters)
- **Vocab**: `rnn_url_vocab.json` (chars: !, $, %, &, ..., a-z, 0-9, etc.)
- **Processing**: Max 256 chars, pad shorter, pad token = 0
- **Threshold**: 0.5 (from `rnn_best_threshold.json`)

**Preprocessing Code:**
```python
def encode_url(url, stoi, max_len=256):
    ids = [stoi.get(ch, 1) for ch in str(url)[:max_len]]
    if len(ids) < max_len:
        ids += [0] * (max_len - len(ids))
    return np.array(ids[:max_len])
```

---

### HTML Model (Transformer)
- **Input**: HTML content → UTF-8 bytes (values 0-255)
- **Vocab**: 259 tokens (0-255 bytes + [PAD=256, CLS=257, SEP=258])
- **Processing**: Encode to UTF-8, window into 2048-token chunks with 50% overlap
- **Multi-window**: Average logits from 4 windows
- **Threshold**: 0.34 (from `transformer_best_threshold.json`)

**Preprocessing Code:**
```python
def to_byte_ids_windowed(text, max_len=2048):
    b = text.encode("utf-8", errors="ignore")
    # Window with overlap or head crop
    ids = [CLS_ID] + list(b[:max_len-2]) + [SEP_ID]
    return np.array(ids)
```

---

### DOM Model (GCN)
- **Input**: DOM tree with nodes, edges, attributes
- **Node Features**: 
  - Tag one-hot (64 tags: div, a, img, form, input, etc.)
  - Degree log, has_href, has_src, is_input, is_password, text_len_log
  - Total: 70 features per node
- **Processing**: Build sparse adjacency matrix, add self-loops, bidirectional edges
- **Threshold**: 0.54 (from `gnn_best_threshold.json`)

**Preprocessing Code:**
```python
def build_graph_tensors(record, tag2id, max_nodes=2048):
    nodes = record.get("nodes", [])
    edges = normalize_edges(record.get("edges"), len(nodes))
    
    # Node features: tag_one_hot + deg_log + attributes
    X = vstack([node_feats_from_any(nd, tag2id) for nd in nodes])
    
    # Adjacency: sparse COO format
    A = sparse_coo_tensor_from_edges(edges, len(nodes))
    
    return X, A, label
```

## 💡 Usage Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# Check URL
response = requests.post(
    f"{BASE_URL}/api/check_url",
    json={"url": "https://suspicious-bank.com"}
)
result = response.json()
print(f"Phishing probability: {result['probability']:.2%}")
print(f"Label: {result['label']}")

# Check HTML
html = """
<html>
<body>
  <a href="http://phishing-site.com">Verify your account</a>
</body>
</html>
"""
response = requests.post(f"{BASE_URL}/api/check_html", json={"html": html})
print(response.json())

# Check DOM
dom_record = {
    "nodes": [
        {"tag": "html"},
        {"tag": "body"},
        {"tag": "form", "attrs": {"action": "http://attacker.com"}},
        {"tag": "input", "attrs": {"type": "password"}}
    ],
    "edges": [[0, 1], [1, 2], [2, 3]],
    "label": 0
}
response = requests.post(f"{BASE_URL}/api/check_dom", json={"dom": dom_record})
print(response.json())
```

### JavaScript/TypeScript Client

```typescript
const BASE_URL = 'http://localhost:8000';

async function checkUrl(url: string) {
  const response = await fetch(`${BASE_URL}/api/check_url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  return response.json();
}

async function checkHtml(html: string) {
  const response = await fetch(`${BASE_URL}/api/check_html`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ html })
  });
  return response.json();
}

// Usage
const result = await checkUrl('https://suspicious.com');
console.log(`Label: ${result.label}`);
```

## 🔗 Integration with Frontend

The frontend should:
1. Capture user input (URL, HTML, DOM)
2. Send POST request to backend API
3. Display result (label + confidence)

Example flow:
```
[User enters URL] 
    → [POST /api/check_url_fast]
    → [Backend: RNN inference ~20ms]
    → [Return: probability + label]
    → [Display: ✅ BENIGN or ⚠️ PHISHING]
```

## 🛠️ Troubleshooting

### Models not loading
- Check CKPT folder exists at `../CKPT`
- Verify checkpoint files: `*.pt`, `*.json`
- Check file paths in `config.py`

### Out of memory
- Reduce batch size in config
- Use CPU instead of CUDA: `DEVICE = "cpu"`
- Reduce `max_nodes` for DOM processing

### Slow inference
- URL: Very fast (~10ms)
- HTML: Faster with single window, slower with multi-window
- DOM: Slowest (depends on graph size)

Optimize by:
- Reducing `max_windows` in `check_html()`
- Using `infer_single()` instead of `infer_multi()`
- Deploying on GPU (CUDA)

## 📈 Performance

Typical latencies (on GPU):
- URL: 10-50ms
- HTML (single): 50-100ms
- HTML (multi): 200-500ms
- DOM: 100-500ms (depends on node count)
- Ensemble: 300-1000ms

Throughput (batch=1):
- ~20 URLs/sec
- ~10 HTML/sec
- ~5 ensemble/sec

## 📝 Model Training

See parent notebook for training details:
```
../datn-phishing-fine-tuning-update.ipynb
```

## 🤝 Contributing

To add a new model:
1. Add architecture to `models_src/architectures.py`
2. Add preprocessing to `models_src/preprocessing.py`
3. Add loader to `models_src/inference.py`
4. Add endpoint to `main.py`

## 📄 License

[Your License Here]

## ✉️ Contact

For issues or questions, contact: [Your Email]
