"""
Configuration for Phishing URL Guardian Backend
"""
import os
from pathlib import Path

# ============ Paths ============
BACKEND_ROOT = Path(__file__).parent
PROJECT_ROOT = BACKEND_ROOT.parent
CKPT_DIR = PROJECT_ROOT / "CKPT"

# Ensure CKPT dir exists
assert CKPT_DIR.exists(), f"[ERROR] CKPT directory not found at {CKPT_DIR}"

# ============ Model Paths ============
# RNN (URL)
RNN_CKPT = CKPT_DIR / "rnn_best_ema.pt"
RNN_URL_VOCAB = CKPT_DIR / "rnn_url_vocab.json"
RNN_THRESHOLD_JSON = CKPT_DIR / "rnn_best_threshold.json"

# Transformer (HTML)
TRANSFORMER_CKPT = CKPT_DIR / "transformer_byte_best.pt"
TRANSFORMER_THRESHOLD_JSON = CKPT_DIR / "transformer_best_threshold.json"

# GNN (DOM)
GNN_CKPT = CKPT_DIR / "gnn_best.pt"
GNN_TAG_VOCAB = CKPT_DIR / "gnn_tag_vocab.json"
GNN_THRESHOLD_JSON = CKPT_DIR / "gnn_best_threshold.json"
GNN_THRESHOLD_CALIBRATED_JSON = CKPT_DIR / "gnn_best_threshold_calibrated.json"

# ============ Model Configs ============
# RNN Configs
RNN_CONFIG = {
    "vocab_size": 87,  # Will be loaded from rnn_url_vocab.json
    "emb_dim": 64,
    "hidden_dim": 128,
    "num_layers": 1,
    "bidir": True,
    "max_len": 256,
}

# Transformer Configs (HTML)
TRANSFORMER_CONFIG = {
    "vocab_size": 259,  # 0..255 + [PAD=256, CLS=257, SEP=258]
    "pad_id": 256,
    "cls_id": 257,
    "sep_id": 258,
    "max_len": 2048,
    "d_model": 192,
    "n_head": 6,
    "n_layers": 4,
    "ffn_dim": 512,
    "dropout": 0.20,
}

# GNN Configs (DOM)
GNN_CONFIG = {
    "tag_topk": 64,
    "max_nodes": 2048,
    "in_dim": None,  # Will be computed from tag vocab + extras
    "hidden_dim": 128,
    "dropout": 0.20,
}

# ============ Device ============
import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Using device: {DEVICE}")

# ============ API Configs ============
API_HOST = "0.0.0.0"
API_PORT = int(os.environ.get("PORT", 8002))  # Railway assigns PORT env var
API_WORKERS = 1

# ============ Logging ============
LOG_LEVEL = "INFO"
