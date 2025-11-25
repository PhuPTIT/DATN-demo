"""
Test script for full phishing detection pipeline
Tests all 3 models + ensemble + new features
"""
import requests
import json
import time

API_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("\n=== TEST 1: Health Check ===")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"✅ Health check passed: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def test_analyze_url_full():
    """Test full URL analysis with all 3 models"""
    print("\n=== TEST 2: Full URL Analysis ===")
    
    test_urls = [
        ("https://www.facebook.com", "BENIGN"),
        ("https://www.google.com", "BENIGN"),
        ("https://paypa1-verify.tk", "PHISHING"),
        ("https://example-bank-login.ml", "PHISHING"),
    ]
    
    for url, expected in test_urls:
        try:
            print(f"\n  Testing: {url}")
            response = requests.post(
                f"{API_URL}/api/analyze_url_full",
                json={"url": url, "normalize": True},
                timeout=20
            )
            
            if response.status_code != 200:
                print(f"  ❌ Status {response.status_code}: {response.text}")
                continue
            
            data = response.json()
            
            # Check URL model
            url_model = data.get("url_model", {})
            print(f"  🔗 URL Model: {url_model.get('label')} ({url_model.get('probability', 0):.2%})")
            print(f"    Confidence: {url_model.get('confidence', 0):.0%}")
            print(f"    Explanations: {len(url_model.get('explanations', []))} reasons provided")
            
            # Check HTML model
            html_model = data.get("html_model", {})
            print(f"  📄 HTML Model: {html_model.get('label')} ({html_model.get('probability', 0):.2%})")
            print(f"    Confidence: {html_model.get('confidence', 0):.0%}")
            
            # Check DOM model
            dom_model = data.get("dom_model", {})
            print(f"  🌳 DOM Model: {dom_model.get('label')} ({dom_model.get('probability', 0):.2%})")
            print(f"    Confidence: {dom_model.get('confidence', 0):.0%}")
            
            # Check Ensemble
            ensemble = data.get("ensemble", {})
            print(f"  🎯 Ensemble: {ensemble.get('label')} ({ensemble.get('probability', 0):.2%})")
            print(f"    Confidence: {ensemble.get('confidence', 0):.0%}")
            
            if ensemble.get("label") == expected:
                print(f"  ✅ PASS (expected {expected})")
            else:
                print(f"  ⚠️  Got {ensemble.get('label')}, expected {expected}")
        
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_batch_analysis():
    """Test batch URL analysis"""
    print("\n=== TEST 3: Batch Analysis ===")
    
    urls = [
        "https://www.google.com",
        "https://www.facebook.com",
        "https://www.google.com",  # Should use cache
        "https://example-phishing.tk",
    ]
    
    try:
        start = time.time()
        response = requests.post(
            f"{API_URL}/api/batch_analyze_urls",
            json={"urls": urls, "normalize": True},
            timeout=60
        )
        elapsed = time.time() - start
        
        if response.status_code != 200:
            print(f"❌ Status {response.status_code}: {response.text}")
            return
        
        data = response.json()
        print(f"  ✅ Processed {data.get('total')} URLs in {elapsed:.1f}s")
        print(f"  Successful: {data.get('successful')}/{data.get('total')}")
        
        # Check cache
        cache_response = requests.post(f"{API_URL}/api/cache_stats")
        cache_data = cache_response.json()
        print(f"  Cache: {cache_data.get('active_cached')} active entries")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def test_error_handling():
    """Test error handling and graceful fallback"""
    print("\n=== TEST 4: Error Handling ===")
    
    test_cases = [
        ("", "Empty URL"),
        ("not-a-url", "Invalid URL"),
        ("https://this-domain-definitely-does-not-exist-12345.com", "Unreachable domain"),
    ]
    
    for url, desc in test_cases:
        try:
            print(f"\n  {desc}: {url}")
            response = requests.post(
                f"{API_URL}/api/analyze_url_full",
                json={"url": url, "normalize": True},
                timeout=15
            )
            
            if response.status_code == 400:
                print(f"  ✅ Correctly rejected: {response.json().get('detail')}")
            elif response.status_code == 200:
                data = response.json()
                html_label = data.get("html_model", {}).get("label")
                if html_label == "UNKNOWN":
                    print(f"  ✅ Graceful fallback: HTML model returned UNKNOWN")
                else:
                    print(f"  ⚠️  Got {html_label}")
            else:
                print(f"  Status: {response.status_code}")
        
        except Exception as e:
            print(f"  ✅ Handled: {type(e).__name__}")

def test_confidence_calculation():
    """Test confidence score calculation"""
    print("\n=== TEST 5: Confidence Scores ===")
    
    urls = [
        "https://www.google.com",  # Should have high confidence (low probability)
        "https://paypa1-verify.tk",  # Should have high confidence (high probability)
    ]
    
    for url in urls:
        try:
            response = requests.post(
                f"{API_URL}/api/analyze_url_full",
                json={"url": url, "normalize": True},
                timeout=20
            )
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            ensemble = data.get("ensemble", {})
            
            prob = ensemble.get("probability", 0)
            conf = ensemble.get("confidence", 0)
            
            print(f"\n  {url}")
            print(f"  Probability: {prob:.2%}, Confidence: {conf:.0%}")
            
            # Confidence should be high when far from threshold (0.5)
            distance_from_threshold = abs(prob - 0.5)
            if conf > 0.5:
                print(f"  ✅ Good confidence (distance from threshold: {distance_from_threshold:.2f})")
            else:
                print(f"  ⚠️  Low confidence")
        
        except Exception as e:
            print(f"  ❌ Error: {e}")

def main():
    print("=" * 60)
    print("URL Guardian - Full Pipeline Test")
    print("=" * 60)
    
    # Check if backend is running
    try:
        requests.get(f"{API_URL}/health", timeout=2)
    except:
        print("\n❌ Backend not running! Start it with: python start_backend.py")
        return
    
    test_health()
    test_analyze_url_full()
    test_batch_analysis()
    test_error_handling()
    test_confidence_calculation()
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
