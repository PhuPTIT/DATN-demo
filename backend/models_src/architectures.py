"""
Model Architecture Definitions (PyTorch)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


# ============ RNN Model (URL) ============
class GRUUrl(nn.Module):
    """GRU model for URL sequence encoding"""
    def __init__(self, vocab_size, emb_dim=64, hidden_dim=128, num_layers=1, bidir=True):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.rnn = nn.GRU(
            emb_dim, hidden_dim, 
            num_layers=num_layers, 
            batch_first=True, 
            bidirectional=bidir
        )
        out_dim = hidden_dim * (2 if bidir else 1)
        self.head = nn.Sequential(
            nn.Linear(out_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 2)
        )
    
    def forward(self, x):
        """
        Args:
            x: (B, L) - batch of encoded URLs
        Returns:
            logits: (B, 2) - class logits
        """
        e = self.emb(x)
        _, h = self.rnn(e)  # h: (layers*dirs, B, H)
        h = torch.cat(list(h), dim=-1)  # concat layers/directions
        return self.head(h)


# ============ Transformer Model (HTML) ============
class ByteTransformer(nn.Module):
    """Transformer encoder for HTML byte sequences"""
    def __init__(
        self, 
        vocab_size=259, 
        d_model=192, 
        nhead=6, 
        num_layers=4, 
        dim_feedforward=512, 
        dropout=0.20,
        pad_id=256
    ):
        super().__init__()
        self.pad_id = pad_id
        self.embed = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.pos = nn.Embedding(4096, d_model)  # positional embeddings (up to 4096 tokens)
        
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
            norm_first=True
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(dropout)
        self.head = nn.Linear(d_model, 2)
        
        # Init
        nn.init.trunc_normal_(self.embed.weight, std=0.02)
        nn.init.trunc_normal_(self.pos.weight, std=0.02)
    
    def forward(self, ids, attn):
        """
        Args:
            ids: (B, L) - batch of byte token IDs
            attn: (B, L) - attention mask (1 = valid, 0 = pad)
        Returns:
            logits: (B, 2) - class logits
        """
        B, L = ids.size()
        pos = torch.arange(L, device=ids.device).unsqueeze(0).expand(B, L)
        x = self.embed(ids) + self.pos(pos)
        
        key_pad = (attn == 0)
        h = self.encoder(x, src_key_padding_mask=key_pad)
        h = self.norm(h)
        
        # Global average pooling with attention
        mask = attn.unsqueeze(-1)
        h = (h * mask).sum(1) / mask.sum(1).clamp(min=1)
        
        return self.head(self.drop(h))


# ============ GNN Model (DOM) ============
class SparseGCNLayer(nn.Module):
    """Sparse Graph Convolutional Layer for DOM graphs"""
    def __init__(self, in_dim, out_dim, dropout=0.1):
        super().__init__()
        self.lin = nn.Linear(in_dim, out_dim, bias=False)
        self.dropout = nn.Dropout(dropout)
        self.eps = 1e-9
    
    def forward(self, X, A):
        """
        Args:
            X: (N, in_dim) - node features
            A: sparse_coo_tensor (N, N) - adjacency matrix
        Returns:
            h: (N, out_dim) - updated node features
        """
        # Normalize: D^(-1/2) A D^(-1/2)
        deg = torch.sparse.sum(A, dim=1).to_dense().clamp(min=self.eps).float()
        d_inv_sqrt = 1.0 / deg.sqrt()
        
        idx = A.indices()
        val = A.values().float()
        v = val * d_inv_sqrt[idx[0]] * d_inv_sqrt[idx[1]]
        A_hat = torch.sparse_coo_tensor(idx, v, A.size(), device=A.device).coalesce()
        
        # Sparse MM
        with torch.amp.autocast('cuda', enabled=False):  # sparse.mm doesn't support AMP well
            AX = torch.sparse.mm(A_hat, X.float())
        AX = AX.to(self.lin.weight.dtype)
        
        return self.dropout(F.relu(self.lin(AX)))


class GCNClassifier(nn.Module):
    """GCN-based classifier for DOM graphs"""
    def __init__(self, in_dim, hid=128, out_dim=2, dropout=0.20):
        super().__init__()
        self.g1 = SparseGCNLayer(in_dim, hid, dropout)
        self.g2 = SparseGCNLayer(hid, hid, dropout)
        self.res = nn.Linear(in_dim, hid, bias=False)  # residual
        self.norm = nn.LayerNorm(hid)
        self.cls = nn.Linear(2 * hid, out_dim)  # [mean, max] readout
    
    def forward(self, X, A, ptr):
        """
        Args:
            X: (N_total, in_dim) - all node features (batch concatenated)
            A: sparse_coo_tensor (N_total, N_total) - block diagonal adjacency
            ptr: (B+1,) - graph pointers (e.g., [0, n1, n1+n2, ...])
        Returns:
            logits: (B, 2) - class logits
        """
        h1 = self.g1(X, A)
        h2 = self.g2(h1, A) + self.res(X)[:h1.size(0)]
        h = self.norm(h2)
        
        # Graph-level readout (mean + max pooling)
        outs = []
        for i in range(len(ptr) - 1):
            s, e = ptr[i], ptr[i + 1]
            g = h[s:e]
            if g.size(0) > 0:
                outs.append(torch.cat([g.mean(0), g.max(0).values], dim=-1))
            else:
                outs.append(torch.zeros(2 * h.size(1), device=X.device))
        
        H = torch.stack(outs, 0)
        return self.cls(H)
