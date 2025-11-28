import sys
sys.path.insert(0, '.')

from config import DEVICE, RNN_CKPT, RNN_URL_VOCAB, RNN_THRESHOLD_JSON
from models_src.inference import UrlModelWrapper
from pydantic import BaseModel

class UrlCheckRequest(BaseModel):
    url: str
    normalize: bool = True

class CheckResponse(BaseModel):
    probability: float
    label: str
    confidence: float

# Load model
url_model = UrlModelWrapper(RNN_CKPT, RNN_URL_VOCAB, RNN_THRESHOLD_JSON, DEVICE)

# Simulate request
request = UrlCheckRequest(url='https://www.facebook.com/watch/?ref=tab')

url = request.url.strip()
print(f"URL: {url}")
print(f"normalize flag: {request.normalize}")

p_phish, label = url_model.infer(url, normalize=request.normalize)
print(f"Prediction: {p_phish:.4f}, Label: {label}")

threshold = url_model.threshold
if label == "PHISHING":
    confidence = min(1.0, p_phish / max(threshold, 0.01))
else:
    confidence = min(1.0, (1 - p_phish) / max(1 - threshold, 0.01))

response = CheckResponse(probability=float(p_phish), label=label, confidence=float(confidence))
print(f"Response: {response}")
