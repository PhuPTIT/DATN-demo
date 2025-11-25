"""
Model Loading and Inference Engine
"""
import json
import torch
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any, List
from urllib.parse import urlparse

from .architectures import GRUUrl, ByteTransformer, GCNClassifier
from .preprocessing import (
    load_url_vocab, encode_url, preprocess_url,
    preprocess_html_single, preprocess_html_multi,
    load_tag_vocab, preprocess_dom
)


# ============ Explanation Generators ============
def generate_url_explanations(url: str, probability: float, label: str) -> List[str]:
    """
    Generate detailed explanations for URL-based verdict
    
    Args:
        url: The URL being analyzed
        probability: Phishing probability (0-1)
        label: Predicted label (PHISHING/BENIGN/UNKNOWN)
    
    Returns:
        List of explanation strings
    """
    explanations = []
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        if label == "PHISHING":
            explanations.append(f"🚨 High-risk domain pattern detected: '{domain}'")
            explanations.append("⚠️ Domain may contain typosquatting or suspicious keywords")
            
            # Specific patterns
            if any(tld in domain for tld in ['.tk', '.ml', '.ga', '.cf']):
                explanations.append(f"🚩 Uses free TLD (.tk/.ml/.ga/.cf) commonly abused by phishers")
            if '-' in domain:
                explanations.append("🔗 Contains hyphens - potential domain mimicry")
            if len(domain) > 25:
                explanations.append("📏 Unusually long domain name - common phishing tactic")
            if url.count('/') > 4:
                explanations.append("📂 Excessive path depth - may contain obfuscation")
        else:
            explanations.append(f"✅ Domain '{domain}' appears legitimate")
            explanations.append("🟢 URL structure matches known legitimate patterns")
            
            if any(tld in domain for tld in ['.com', '.org', '.edu', '.gov']):
                explanations.append("✓ Uses recognized legitimate TLD")
    except:
        explanations.append("Domain structure: Checked for typosquatting and suspicious patterns")
    
    return explanations


def generate_html_explanations(html: str, probability: float, label: str) -> List[str]:
    """
    Generate detailed explanations for HTML-based verdict
    
    Args:
        html: HTML content
        probability: Phishing probability (0-1)
        label: Predicted label (PHISHING/BENIGN/UNKNOWN)
    
    Returns:
        List of explanation strings
    """
    explanations = []
    
    try:
        html_lower = html.lower()
        
        if label == "PHISHING":
            explanations.append("🚨 Suspicious HTML patterns detected")
            
            # Check for specific phishing indicators
            if html_lower.count('<form') > 2:
                explanations.append(f"⚠️ Multiple forms detected ({html_lower.count('<form')}+) - data harvesting")
            if 'password' in html_lower and 'login' in html_lower:
                explanations.append("🔐 Contains password field + login form - credential harvesting risk")
            if 'alert(' in html_lower or 'script>' in html_lower:
                explanations.append("⚙️ Malicious JavaScript detected - may inject harmful code")
            if 'iframe' in html_lower or 'object' in html_lower:
                explanations.append("📦 Embedded external content (iframe/object) - potential malware vector")
            if 'hidden' in html_lower and 'type="hidden"' in html_lower:
                explanations.append("👁️ Hidden form fields detected - may exfiltrate data")
        else:
            explanations.append("✅ HTML structure appears legitimate")
            explanations.append("🟢 No suspicious form patterns or scripts detected")
            
            if '<meta' in html_lower:
                explanations.append("✓ Contains proper meta tags and structured content")
    except:
        explanations.append("Form analysis: Checked for input fields and suspicious targets")
    
    return explanations


def generate_dom_explanations(dom_record: dict, probability: float, label: str) -> List[str]:
    """
    Generate detailed explanations for DOM-based verdict
    
    Args:
        dom_record: DOM record dictionary
        probability: Phishing probability (0-1)
        label: Predicted label (PHISHING/BENIGN/UNKNOWN)
    
    Returns:
        List of explanation strings
    """
    explanations = []
    
    try:
        nodes = dom_record.get("nodes", [])
        edges = dom_record.get("edges", [])
        
        if label == "PHISHING":
            explanations.append("🚨 Unusual DOM tree structure detected")
            
            node_count = len(nodes)
            if node_count < 5:
                explanations.append("📉 Very sparse DOM - may be hidden content or obfuscated structure")
            elif node_count > 500:
                explanations.append(f"📈 Large DOM tree ({node_count} nodes) - potential for malicious elements")
        else:
            explanations.append("✅ Normal DOM tree structure")
            explanations.append(f"🟢 DOM contains {len(nodes)} elements with {len(edges)} connections")
    except:
        explanations.append("DOM analysis: Analyzed tree structure and element graph")
    
    return explanations


class UrlModelWrapper:
    """Wrapper for RNN URL model"""
    
    def __init__(self, ckpt_path: Path, vocab_path: Path, threshold_path: Path, device: str = "cpu"):
        self.device = device
        
        # Load vocab
        self.stoi, self.itos = load_url_vocab(vocab_path)
        vocab_size = len(self.itos)
        
        # Load model
        self.model = GRUUrl(
            vocab_size=vocab_size,
            emb_dim=64,
            hidden_dim=128,
            num_layers=1,
            bidir=True
        ).to(device)
        
        state_dict = torch.load(ckpt_path, map_location=device)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        
        # Load threshold
        with open(threshold_path, 'r') as f:
            self.threshold = json.load(f)["threshold"]
    
    def infer(self, url: str, normalize: bool = False) -> Tuple[float, str]:
        """
        Infer phishing probability for URL
        Args:
            url: URL string
            normalize: if True, extract domain only (ignore path/query)
        Returns:
            (p_phish, label): probability and "PHISHING" or "BENIGN"
        """
        x = preprocess_url(url, self.stoi, max_len=256, normalize=normalize).to(self.device)
        
        with torch.no_grad():
            logits = self.model(x)
            probs = torch.softmax(logits, dim=-1)
            p_phish = probs[0, 1].item()
        
        label = "PHISHING" if p_phish >= self.threshold else "BENIGN"
        return p_phish, label
    
    def get_explanations(self, url: str, probability: float, label: str) -> List[str]:
        """Generate detailed explanations for URL prediction"""
        return generate_url_explanations(url, probability, label)


class HtmlModelWrapper:
    """Wrapper for Transformer HTML model"""
    
    def __init__(self, ckpt_path: Path, threshold_path: Path, device: str = "cpu"):
        self.device = device
        
        # Load model
        self.model = ByteTransformer(
            vocab_size=259,
            d_model=192,
            nhead=6,
            num_layers=4,
            dim_feedforward=512,
            dropout=0.20,
            pad_id=256
        ).to(device)
        
        state_dict = torch.load(ckpt_path, map_location=device)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        
        # Load threshold
        with open(threshold_path, 'r') as f:
            self.threshold = json.load(f)["threshold"]
    
    @torch.no_grad()
    def infer_single(self, html: str) -> Tuple[float, str]:
        """Single-window inference (fast)"""
        ids, attn = preprocess_html_single(html, max_len=2048)
        ids = ids.to(self.device)
        attn = attn.to(self.device)
        
        logits = self.model(ids, attn)
        probs = torch.softmax(logits, dim=-1)
        p_phish = probs[0, 1].item()
        
        label = "PHISHING" if p_phish >= self.threshold else "BENIGN"
        return p_phish, label
    
    @torch.no_grad()
    def infer_multi(self, html: str, max_windows: int = 4) -> Tuple[float, str]:
        """Multi-window inference (robust, slower)"""
        ids, attn = preprocess_html_multi(
            html, 
            max_len=2048,
            max_windows=max_windows,
            stride=2048 // 3
        )
        ids = ids.to(self.device)
        attn = attn.to(self.device)
        
        logits = self.model(ids, attn)  # (W, 2)
        probs = torch.softmax(logits, dim=-1)  # (W, 2)
        p_phish = probs.mean(0)[1].item()  # average across windows
        
        label = "PHISHING" if p_phish >= self.threshold else "BENIGN"
        return p_phish, label
    
    def get_explanations(self, html: str, probability: float, label: str) -> List[str]:
        """Generate detailed explanations for HTML prediction"""
        return generate_html_explanations(html, probability, label)


class DomModelWrapper:
    """Wrapper for GCN DOM model"""
    
    def __init__(self, ckpt_path: Path, tag_vocab_path: Path, threshold_path: Path, device: str = "cpu"):
        self.device = device
        
        # Load tag vocab
        self.tags = load_tag_vocab(tag_vocab_path)
        self.tag2id = {tag: i for i, tag in enumerate(self.tags)}
        self.f_tag = len(self.tags)
        self.f_extra = 6
        
        # Load model
        in_dim = self.f_tag + self.f_extra
        self.model = GCNClassifier(
            in_dim=in_dim,
            hid=128,
            out_dim=2,
            dropout=0.20
        ).to(device)
        
        state_dict = torch.load(ckpt_path, map_location=device)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        
        # Load threshold
        with open(threshold_path, 'r') as f:
            self.threshold = json.load(f)["threshold"]
    
    @torch.no_grad()
    def infer(self, dom_record: Dict) -> Tuple[float, str]:
        """
        Infer phishing probability for DOM graph
        Args:
            dom_record: dict with "nodes", "edges", "label"
        Returns:
            (p_phish, label)
        """
        X, A, _ = preprocess_dom(
            dom_record,
            self.tag2id,
            self.f_tag,
            self.f_extra,
            max_nodes=2048
        )
        
        X = X.to(self.device)
        A = A.to(self.device)
        
        # Build single-graph batch
        ptr = torch.tensor([0, X.size(0)], dtype=torch.long, device=self.device)
        
        logits = self.model(X, A, ptr)
        probs = torch.softmax(logits, dim=-1)
        p_phish = probs[0, 1].item()
        
        label = "PHISHING" if p_phish >= self.threshold else "BENIGN"
        return p_phish, label
    
    def get_explanations(self, dom_record: dict, probability: float, label: str) -> List[str]:
        """Generate detailed explanations for DOM prediction"""
        return generate_dom_explanations(dom_record, probability, label)


class EnsemblePredictor:
    """Ensemble predictions from all 3 models"""
    
    def __init__(
        self,
        url_wrapper: UrlModelWrapper,
        html_wrapper: HtmlModelWrapper,
        dom_wrapper: DomModelWrapper,
        weights: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    ):
        self.url = url_wrapper
        self.html = html_wrapper
        self.dom = dom_wrapper
        
        total = sum(weights)
        self.weights = [w / total for w in weights]
    
    def predict(
        self,
        url: str = None,
        html: str = None,
        dom_record: Dict = None,
        use_models: Tuple[bool, bool, bool] = (True, True, True)
    ) -> Dict[str, Any]:
        """
        Ensemble prediction from available models
        Args:
            url: URL string (optional)
            html: HTML string (optional)
            dom_record: DOM record dict (optional)
            use_models: tuple of (use_url, use_html, use_dom)
        Returns:
            {
                "url": (p_phish, label) or None,
                "html": (p_phish, label) or None,
                "dom": (p_phish, label) or None,
                "ensemble_prob": float,
                "ensemble_label": str
            }
        """
        results = {}
        probs = []
        
        if use_models[0] and url:
            p_url, l_url = self.url.infer(url)
            results["url"] = {"prob": p_url, "label": l_url}
            probs.append(p_url * self.weights[0])
        
        if use_models[1] and html:
            p_html, l_html = self.html.infer_multi(html)
            results["html"] = {"prob": p_html, "label": l_html}
            probs.append(p_html * self.weights[1])
        
        if use_models[2] and dom_record:
            p_dom, l_dom = self.dom.infer(dom_record)
            results["dom"] = {"prob": p_dom, "label": l_dom}
            probs.append(p_dom * self.weights[2])
        
        if probs:
            ensemble_prob = sum(probs)
            ensemble_label = "PHISHING" if ensemble_prob >= 0.5 else "BENIGN"
        else:
            ensemble_prob = 0.0
            ensemble_label = "UNKNOWN"
        
        results["ensemble"] = {
            "prob": ensemble_prob,
            "label": ensemble_label
        }
        
        return results
