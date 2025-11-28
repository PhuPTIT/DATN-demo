# 🧪 TEST GUIDE: Phân Tích HTML + DOM Thực

## ✅ Pre-Test Checklist

- [ ] Backend code updated (`backend/main.py` + endpoint)
- [ ] Dependencies installed (`requests`, `lxml`)
- [ ] Frontend code updated (`src/pages/Index.tsx`)
- [ ] No TypeScript errors in IDE
- [ ] Backend and Frontend ready to run

---

## 🚀 Step-by-Step Test

### **Setup Phase (Lần Đầu)**

#### **Step 1: Install Backend Dependencies**
```powershell
cd "c:\Users\PTC\Downloads\url-guardian-demo-main\url-guardian-demo-main\backend"
pip install requests lxml
```

#### **Step 2: Start Backend Server**
```powershell
# Terminal 1
cd backend
python main.py

# Expect:
# [INFO] Loading models...
# [OK] URL model (RNN) loaded
# [OK] HTML model (Transformer) loaded
# [OK] DOM model (GCN) loaded
# [OK] Ensemble predictor created
# INFO: Uvicorn running on http://0.0.0.0:8000
```

**Verify Backend:**
```powershell
# Terminal (another window)
curl -X GET http://localhost:8000/
# Should return: {"message": "URL Guardian Backend is running", ...}
```

#### **Step 3: Start Frontend Server**
```powershell
# Terminal 2
cd "c:\Users\PTC\Downloads\url-guardian-demo-main\url-guardian-demo-main"
npm run dev

# Expect:
# ➜ Local: http://localhost:8081
```

---

### **Test Phase 1: Check Endpoints Work**

#### **Test 1.1: Fetch URL Resources Endpoint**
```powershell
# Terminal 3
$url = "https://www.google.com/"
$body = @{ url = $url } | ConvertTo-Json

$response = Invoke-RestMethod `
  -Uri "http://localhost:8000/api/fetch_url_resources" `
  -Method Post `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body

Write-Host "Response Length: $($response.html.Length) chars"
Write-Host "Success: $($response.success)"
Write-Host "First 200 chars: $($response.html.Substring(0, 200))"
```

**Expected:**
```
Response Length: 5000+ chars
Success: True
First 200 chars: <!doctype html><html...>
```

---

### **Test Phase 2: Frontend UI Test**

#### **Test 2.1: Open Application**
1. Open browser: `http://localhost:8081`
2. Should see form with:
   - URL Input field
   - "Kiểm tra URL" button
   - "Phân tích HTML + DOM" button (disabled)
   - 4 result sections (URL, Liveness, HTML, DOM)

#### **Test 2.2: Test with Legitimate Site**
1. Input URL: `https://www.google.com/`
2. Click "Kiểm tra URL"
3. **Expected Result:**
   - ✅ URL Result shows (low phishing %)
   - ✅ Liveness Status: "Alive"
   - ✅ "Phân tích HTML+DOM" button **enabled**
   - ℹ️ HTML/DOM results still empty

4. Click "Phân tích HTML + DOM"
5. **Wait 5-10 seconds** (backend fetching + analyzing)
6. **Expected Result:**
   - ✅ HTML Result shows (low phishing % for legitimate site)
   - ✅ DOM Result shows (low phishing % for legitimate site)
   - ✅ Both show model confidence

**Example Output:**
```
URL Detection:
├─ BENIGN (8%)
├─ Model: URL RNN
└─ Confidence: 85%

HTML Analysis:
├─ BENIGN (12%)
├─ Model: Transformer (byte-level)
└─ Confidence: 88%

DOM Analysis:
├─ BENIGN (18%)
├─ Model: Graph Convolutional Network (GCN)
└─ Confidence: 90%
```

---

### **Test Phase 3: Determinism Test** ⭐ IMPORTANT

#### **Test 3.1: Run Same URL 3 Times**
1. Input: `https://www.google.com/`
2. Click "Phân tích HTML + DOM"
3. Wait for results
4. **Note down all 3 results:**
   - URL %
   - Liveness status
   - HTML %
   - DOM %

5. Click "Phân tích HTML + DOM" again (2nd time)
6. Note results
7. Click "Phân tích HTML + DOM" again (3rd time)
8. Note results

**Expected (DETERMINISTIC):**
```
Run 1: URL=8%, Liveness=Alive, HTML=12%, DOM=18%
Run 2: URL=8%, Liveness=Alive, HTML=12%, DOM=18%  ← IDENTICAL ✅
Run 3: URL=8%, Liveness=Alive, HTML=12%, DOM=18%  ← IDENTICAL ✅
```

**If Different:** ❌ FAILED - Debug required

---

### **Test Phase 4: Test with Phishing Site**

#### **Test 4.1: Input Phishing URL** (từ dataset của bạn)
```
If you have phishing link from training data:
1. Input that link
2. Click "Kiểm tra URL" 
3. Should show HIGH phishing probability
4. Click "Phân tích HTML + DOM"
5. HTML + DOM should also show HIGH phishing probability
```

**Example Expected:**
```
URL: High % (70-90%)
HTML: High % (60-85%)
DOM: High % (75-90%)
```

---

### **Test Phase 5: Edge Cases**

#### **Test 5.1: Invalid URL**
```
Input: "not-a-url"
Expected: Error message "URL phải bắt đầu bằng 'http://'"
```

#### **Test 5.2: URL with Timeout**
```
Input: https://very-slow-website.com (if exists)
Expected: Error "Cannot reach URL" or timeout message
```

#### **Test 5.3: 404 Page**
```
Input: https://example.com/nonexistent-page
Expected: HTML fetched (404 page HTML), analyzed normally
```

#### **Test 5.4: Very Large Page**
```
Input: Large website with 1000+ DOM nodes
Expected: Truncated to 100 nodes, analyzed normally
```

---

### **Test Phase 6: Browser DevTools Check**

#### **Test 6.1: Check Network Requests**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Click "Phân tích HTML + DOM"
4. Watch requests:
   - [ ] POST to `http://localhost:8000/api/fetch_url_resources`
   - [ ] POST to `http://localhost:8000/api/check_html`
   - [ ] POST to `http://localhost:8000/api/check_dom`

#### **Test 6.2: Check Console for Errors**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Run analysis
4. Check for errors (should be none if working)

---

## 📊 Test Report Template

```
Test Date: _______________
Tester: ___________________
Environment: Windows | Backend: Running | Frontend: Running

PHASE 1: Endpoints ✅/❌
├─ Backend starts without error: ___
├─ Frontend starts without error: ___
├─ /api/fetch_url_resources works: ___
└─ Other endpoints respond: ___

PHASE 2: UI Test ✅/❌
├─ Form displays correctly: ___
├─ URL input field works: ___
├─ "Kiểm tra URL" button works: ___
└─ "Phân tích HTML+DOM" button works: ___

PHASE 3: Determinism ✅/❌
├─ Run 1 Results: URL=_%, HTML=_%, DOM=_%
├─ Run 2 Results: URL=_%, HTML=_%, DOM=_% (Match Run1? ___) 
├─ Run 3 Results: URL=_%, HTML=_%, DOM=_% (Match Run1&2? ___)
└─ Conclusion: DETERMINISTIC? ✅/❌

PHASE 4: Phishing Test ✅/❌
├─ Phishing URL input: ___
├─ URL % (expected high): ___
├─ HTML % (expected high): ___
├─ DOM % (expected high): ___
└─ All high as expected? ✅/❌

PHASE 5: Edge Cases ✅/❌
├─ Invalid URL handled: ___
├─ Timeout handled: ___
├─ 404 page handled: ___
└─ Large page handled: ___

PHASE 6: DevTools Check ✅/❌
├─ Network requests visible: ___
├─ No console errors: ___
├─ Response times reasonable: ___
└─ All payloads valid JSON: ___

Overall Result: ✅ PASS / ⚠️ PARTIAL / ❌ FAIL

Issues Found:
1. _________________________________
2. _________________________________
3. _________________________________

Notes:
_________________________________
_________________________________
```

---

## 🐛 Troubleshooting

### **Issue: "Cannot find name 'getMockHtmlContent'"**
- **Cause:** Frontend code still has old function calls
- **Fix:** Ensure `src/pages/Index.tsx` is updated with new functions
- **Verify:** Search for `getMockHtmlContent` - should not exist

### **Issue: "POST /api/fetch_url_resources not found"**
- **Cause:** Backend endpoint not added
- **Fix:** Check `backend/main.py` for new endpoint
- **Verify:** Backend logs show `[OK] Ensemble predictor created`

### **Issue: "requests module not found"**
- **Cause:** Dependencies not installed
- **Fix:** Run `pip install requests lxml`
- **Verify:** `python -c "import requests; print('OK')"`

### **Issue: Network Error / Cannot reach URL**
- **Cause:** Website blocked requests or timeout
- **Fix:** Try different URL or increase timeout
- **Verify:** Website is accessible from browser

### **Issue: Results differ each run (Not Deterministic)**
- **Cause:** Still using random generation somewhere
- **Fix:** Verify no `Math.random()` in analyzeHtmlDom
- **Verify:** Backend models run with `model.eval()` + `torch.no_grad()`

### **Issue: HTML/DOM results always same (even for different URLs)**
- **Cause:** Cache or not actually fetching new HTML
- **Fix:** Clear browser cache (Ctrl+Shift+Delete)
- **Verify:** Check network tab shows different HTML responses

---

## ✅ Success Criteria

- [ ] Backend + Frontend start without errors
- [ ] `/api/fetch_url_resources` endpoint works
- [ ] Frontend can fetch HTML from URL
- [ ] HTML → DOM conversion works
- [ ] 3 runs of same URL → identical results
- [ ] Phishing URLs show high % across all models
- [ ] No console errors in browser
- [ ] Network requests visible in DevTools
- [ ] Response times < 10 seconds per analysis

---

## 📈 Performance Baseline

Expected timing for `https://www.google.com/`:
- URL Check: ~200ms (URL model inference)
- Fetch HTML: ~1-2s (network)
- HTML Analysis: ~800ms (Transformer model)
- DOM Analysis: ~600ms (GCN model)
- **Total: ~3-5 seconds**

If significantly slower:
- Check backend CPU usage
- Verify model is on GPU (if available)
- Check network latency

---

## 🎉 After Testing

When all tests pass:
1. ✅ Document results in report above
2. ✅ Take screenshots for portfolio
3. ✅ Review code changes
4. ✅ Commit to git (if applicable)
5. ✅ Move to next feature or optimization
