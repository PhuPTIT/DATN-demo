import sys
sys.path.insert(0, '.')

from config import DEVICE, RNN_CKPT, RNN_URL_VOCAB, RNN_THRESHOLD_JSON
from models_src.inference import UrlModelWrapper

# Load model
url_model = UrlModelWrapper(RNN_CKPT, RNN_URL_VOCAB, RNN_THRESHOLD_JSON, DEVICE)

url1 = 'https://www.facebook.com/'
url2 = 'https://www.facebook.com/watch/?ref=tab'

print("=== With normalize=True (DEFAULT) ===")
p1, label1 = url_model.infer(url1, normalize=True)
p2, label2 = url_model.infer(url2, normalize=True)

print(f"URL1: {url1}")
print(f"  Result: probability={p1:.4f}, label={label1}")

print(f"URL2: {url2}")
print(f"  Result: probability={p2:.4f}, label={label2}")

print(f"\nMatch: {label1 == label2} (both {label1})")
print(f"Probability difference: {abs(p1-p2):.6f}")

if label1 == label2 and label1 == "BENIGN":
    print("\n✓ SUCCESS: URL normalization working correctly!")
    print("Both URLs normalized to same domain, returning identical results.")
else:
    print("\n✗ FAILED: URLs should both be BENIGN with normalize=True")
