"""
Preprocessing utilities for URL, HTML, and DOM inputs
"""
import json
import math
import numpy as np
import torch
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse
import tldextract


# ============ URL Processing (RNN) ============
def load_url_vocab(vocab_path: Path) -> Tuple[Dict, List]:
    """Load URL character vocabulary from JSON"""
    with open(vocab_path, 'r') as f:
        data = json.load(f)
    itos = data["itos"]
    stoi = {c: i for i, c in enumerate(itos)}
    return stoi, itos


def normalize_url_for_model(url: str) -> str:
    """
    Normalize URL for RNN model input.
    Extract scheme, netloc (domain), and port; discard path/query/fragment.
    This ensures same domain always produces same features regardless of path.
    
    Args:
        url: URL string
    Returns:
        normalized URL (scheme + domain + port, no path/query)
    
    Example:
        normalize_url_for_model("https://www.facebook.com/watch/?ref=tab")
        -> "https://www.facebook.com/"
    """
    try:
        parsed = urlparse(url)
        # Reconstruct URL with only scheme, netloc (domain+port), no path/query
        normalized = f"{parsed.scheme}://{parsed.netloc}/"
        return normalized
    except Exception:
        # If parsing fails, return original URL
        return url


def encode_url(url: str, stoi: Dict, max_len: int = 256, normalize: bool = False) -> np.ndarray:
    """
    Encode URL string to character indices
    Args:
        url: URL string
        stoi: string-to-index mapping
        max_len: maximum length
        normalize: if True, extract domain only
    Returns:
        encoded IDs array (max_len,)
    """
    # Normalize URL first if requested (extract domain only)
    if normalize:
        url = normalize_url_for_model(url)
    url_str = str(url)[:max_len]
    ids = [stoi.get(ch, 1) for ch in url_str]  # 1 = <UNK>
    
    # Pad to max_len
    if len(ids) < max_len:
        ids += [0] * (max_len - len(ids))  # 0 = <PAD>
    
    return np.array(ids[:max_len], dtype=np.int32)


def preprocess_url(url: str, stoi: Dict, max_len: int = 256, normalize: bool = True) -> torch.Tensor:
    """
    Preprocess URL for RNN model
    Args:
        url: URL string
        stoi: vocabulary mapping
        max_len: max sequence length
        normalize: if True, extract domain only (ignore path/query) [DEFAULT: True for stable results]
    Returns:
        encoded tensor (1, max_len)
    """
    if normalize:
        url = normalize_url_for_model(url)
    encoded = encode_url(url, stoi, max_len, normalize=False)  # Don't normalize again in encode_url
    return torch.from_numpy(encoded).unsqueeze(0)  # (1, max_len)


# ============ HTML Processing (Transformer) ============
def to_byte_ids_windowed(
    text: str, 
    max_len: int = 2048, 
    pad_id: int = 256, 
    cls_id: int = 257, 
    sep_id: int = 258,
    window: Tuple[int, int] = None,
    random_window: bool = False
) -> np.ndarray:
    """
    Convert HTML text to byte token IDs
    Args:
        text: HTML string
        max_len: maximum sequence length
        pad_id: padding token ID
        cls_id: [CLS] token ID
        sep_id: [SEP] token ID
        window: (start, end) tuple for windowing
        random_window: if True and no window, sample random crop
    Returns:
        token IDs array with [CLS] prepended and [SEP] appended
    """
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    
    # Convert to UTF-8 bytes
    b = text.encode("utf-8", errors="ignore")
    
    # Select window
    if window is None:
        if len(b) <= max_len or not random_window:
            start = 0
        else:
            start = np.random.randint(0, max(1, len(b) - max_len + 1))
        seg = b[start:start + max_len]
    else:
        s, e = window
        seg = b[s:e]
    
    # Build token sequence: [CLS] + bytes + [SEP]
    ids = [cls_id] + list(seg[:max_len - 2]) + [sep_id]
    
    # Map overflow bytes (shouldn't happen for valid UTF-8)
    ids = [x if x < 256 else 0 for x in ids]
    
    return np.asarray(ids, dtype=np.int32)


def make_windows(
    byte_arr: bytes, 
    max_len: int = 2048, 
    stride: int = None, 
    max_windows: int = 4
) -> List[Tuple[int, int]]:
    """
    Create overlapping windows over a byte array
    Args:
        byte_arr: byte sequence
        max_len: window size
        stride: overlap stride (default: max_len/2)
        max_windows: maximum number of windows to return
    Returns:
        list of (start, end) tuples
    """
    L = len(byte_arr)
    if L <= max_len:
        return [(0, L)]
    
    if stride is None:
        stride = max_len // 2  # 50% overlap
    
    starts = list(range(0, max(1, L - max_len + 1), stride))
    
    if len(starts) > max_windows:
        idx = np.linspace(0, len(starts) - 1, num=max_windows).round().astype(int)
        starts = [starts[i] for i in idx]
    
    return [(s, min(s + max_len, L)) for s in starts]


def preprocess_html_single(
    html: str,
    max_len: int = 2048,
    pad_id: int = 256,
    cls_id: int = 257,
    sep_id: int = 258,
    random_window: bool = False
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Preprocess HTML (single window)
    Returns:
        (ids, attention_mask) both of shape (1, seq_len)
    """
    ids = to_byte_ids_windowed(
        html, 
        max_len=max_len, 
        pad_id=pad_id, 
        cls_id=cls_id, 
        sep_id=sep_id,
        random_window=random_window
    )
    
    ids_tensor = torch.tensor(ids, dtype=torch.long).unsqueeze(0)  # (1, L)
    attn = (ids_tensor != pad_id).long()  # (1, L)
    
    return ids_tensor, attn


def preprocess_html_multi(
    html: str,
    max_len: int = 2048,
    pad_id: int = 256,
    cls_id: int = 257,
    sep_id: int = 258,
    max_windows: int = 4,
    stride: int = None
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Preprocess HTML (multi-window for robust inference)
    Returns:
        (ids, attention_mask) both of shape (num_windows, seq_len)
    """
    b = html.encode("utf-8", errors="ignore")
    windows = make_windows(b, max_len, stride=stride, max_windows=max_windows)
    
    id_list = []
    for start, end in windows:
        ids = to_byte_ids_windowed(
            html, 
            max_len=max_len,
            pad_id=pad_id,
            cls_id=cls_id,
            sep_id=sep_id,
            window=(start, end),
            random_window=False
        )
        id_list.append(torch.tensor(ids, dtype=torch.long))
    
    ids_tensor = torch.stack(id_list, dim=0)  # (W, L)
    attn = (ids_tensor != pad_id).long()  # (W, L)
    
    return ids_tensor, attn


# ============ DOM Processing (GNN) ============
def load_tag_vocab(tag_vocab_path: Path) -> List[str]:
    """Load HTML tag vocabulary"""
    with open(tag_vocab_path, 'r') as f:
        data = json.load(f)
    return data["tags"]


def get_tag_from_node(node) -> str:
    """Extract tag name from node dict or string"""
    if isinstance(node, dict):
        return (node.get("tag") or "").lower()
    if isinstance(node, str):
        return node.lower()
    return ""


def node_feats_from_any(
    node, 
    tag2id: Dict,
    f_tag: int,
    f_extra: int = 6
) -> np.ndarray:
    """
    Build feature vector for a DOM node
    Features: [tag_one_hot (f_tag), deg_log, has_href, has_src, is_input, is_pw, text_len_log]
    """
    # Tag one-hot
    tag = get_tag_from_node(node)
    x = np.zeros(f_tag, dtype=np.float32)
    if tag in tag2id:
        x[tag2id[tag]] = 1.0
    
    # Attributes
    attrs = {}
    text_len = 0.0
    if isinstance(node, dict):
        attrs = node.get("attrs") or {}
        text_len = float(node.get("text_len", 0) or attrs.get("text_len", 0) or 0)
    
    has_href = float(attrs.get("href", 0) or attrs.get("has_href", 0) or 0)
    has_src = float(attrs.get("src", 0) or attrs.get("has_src", 0) or 0)
    is_input = float(attrs.get("is_input", 0) or (tag == "input"))
    is_pw = float(attrs.get("is_pw", 0) or (str(attrs.get("type", "")).lower() in ("password", "pwd")))
    tlen_log = math.log1p(max(0.0, text_len))
    
    # deg_log filled later
    extra = np.array([0.0, has_href, has_src, is_input, is_pw, tlen_log], dtype=np.float32)
    
    return np.concatenate([x, extra])


def normalize_edges(edges, n: int) -> List[Tuple[int, int]]:
    """Normalize edge format to list of (u, v) tuples"""
    out = []
    for e in (edges or []):
        u = v = None
        if isinstance(e, (list, tuple)) and len(e) >= 2:
            u, v = int(e[0]), int(e[1])
        elif isinstance(e, dict):
            u = e.get("src", e.get("u"))
            v = e.get("dst", e.get("v"))
            if u is not None and v is not None:
                u, v = int(u), int(v)
        
        if u is None or v is None:
            continue
        if 0 <= u < n and 0 <= v < n:
            out.append((u, v))
    
    return out


def build_graph_tensors(
    record: Dict,
    tag2id: Dict,
    f_tag: int,
    f_extra: int = 6,
    max_nodes: int = 2048
) -> Tuple[torch.Tensor, torch.sparse_coo_tensor, torch.Tensor]:
    """
    Build graph tensors from DOM record
    Args:
        record: dict with "nodes", "edges", "label"
        tag2id: tag vocabulary mapping
        f_tag: number of tag features
        f_extra: number of extra features
        max_nodes: max nodes to keep
    Returns:
        (X, A, y): node features, adjacency matrix, label
    """
    nodes = record.get("nodes") or []
    y = int(record.get("label", 0))
    N = len(nodes)
    
    if N == 0:
        X = torch.zeros((1, f_tag + f_extra), dtype=torch.float32)
        A = torch.sparse_coo_tensor(
            torch.tensor([[0], [0]]), 
            torch.tensor([1.0]), 
            (1, 1)
        ).coalesce()
        return X, A, torch.tensor([y], dtype=torch.long)
    
    # Keep top max_nodes
    keep = min(N, max_nodes)
    X_np = np.vstack([
        node_feats_from_any(nd, tag2id, f_tag, f_extra) 
        for nd in nodes[:keep]
    ]).astype(np.float32)
    X = torch.from_numpy(X_np)
    
    # Build edges
    es = normalize_edges(record.get("edges"), N)
    kept = set(range(keep))
    pairs = []
    
    for (u, v) in es:
        if u in kept and v in kept:
            pairs.append((u, v))
            pairs.append((v, u))  # undirected
    
    # Add self-loops
    for i in range(keep):
        pairs.append((i, i))
    
    # Build sparse adjacency
    if pairs:
        idx = torch.tensor(pairs, dtype=torch.long).t()
        vals = torch.ones(idx.size(1), dtype=torch.float32)
        A = torch.sparse_coo_tensor(idx, vals, (keep, keep)).coalesce()
    else:
        idx = torch.arange(keep)
        A = torch.sparse_coo_tensor(
            torch.stack([idx, idx]), 
            torch.ones(keep), 
            (keep, keep)
        ).coalesce()
    
    # Compute and fill degree log
    deg = torch.sparse.sum(A, dim=1).to_dense().unsqueeze(1)
    X[:, f_tag + 0] = deg.squeeze(1).clamp(max=50).log1p()
    
    return X, A, torch.tensor([y], dtype=torch.long)


def preprocess_dom(
    record: Dict,
    tag2id: Dict,
    f_tag: int,
    f_extra: int = 6,
    max_nodes: int = 2048
) -> Tuple[torch.Tensor, torch.sparse_coo_tensor, torch.Tensor]:
    """
    Preprocess DOM graph record
    Returns:
        (X, A, y): node features, adjacency, label
    """
    return build_graph_tensors(record, tag2id, f_tag, f_extra, max_nodes)
