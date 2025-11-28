# 🔍 GIẢI THÍCH: Tại Sao HTML + DOM Cho Kết Quả Sai?

## 📋 Tóm Tắt Vấn Đề

```
✅ URL Model: 100% chính xác (dùng backend API thực)
❌ HTML Model: Kết quả sai
❌ DOM Model: Kết quả sai
```

---

## 🔧 Thao Tác Phân Tích HTML + DOM (Hiện Tại)

### **File: `src/pages/Index.tsx` - Lines 265-289**

```typescript
const analyzeHtmlDom = async () => {
  setHtmlResult(null);
  setDomResult(null);
  setIsAnalyzing(true);

  try {
    // Bước 1: Lấy MOCK DATA cố định
    const htmlContent = getMockHtmlContent();      // ← LỖI Ở ĐÂY! 🔴
    const domRecord = getMockDomRecord();          // ← LỖI Ở ĐÂY! 🔴

    // Bước 2: Gọi backend APIs
    const [htmlRes, domRes] = await Promise.all([
      checkHtmlViaBackend(htmlContent),            // POST /api/check_html
      checkDomViaBackend(domRecord)                // POST /api/check_dom
    ]);

    // Bước 3: Set kết quả
    if (htmlRes) setHtmlResult(htmlRes);
    if (domRes) setDomResult(domRes);

    if (!htmlRes && !domRes) {
      setError("Lỗi: Không thể gọi backend API cho HTML/DOM analysis");
    }
  } catch (err: any) {
    setError("Lỗi khi phân tích HTML/DOM: " + (err.message || String(err)));
  } finally {
    setIsAnalyzing(false);
  }
};
```

---

## ❌ **VẤN ĐỀ 1: HTML Model (Lines 182-187)**

### **Mock HTML Content (SAI):**
```typescript
const getMockHtmlContent = (): string => {
  // Fixed mock HTML content (same every time)
  return `<html>
    <head><title>Sample Page</title></head>
    <body>
      <h1>Welcome</h1>
      <form>
        <input type="email" placeholder="Email" />
        <input type="password" placeholder="Password" />
        <button type="submit">Login</button>
      </form>
      <script src="https://external.cdn.com/script.js"></script>
    </body>
  </html>`;
};
```

### **Tại Sao Sai?** 🔴

1. **HTML là MOCK DATA cố định**, không phải HTML thực từ website
2. **HTML này đơn giản quá**: Chỉ có form + password input = nhìn giống phishing, nhưng không phải
3. **Backend Transformer model được train trên HTML thực từ dataset**:
   - HTML thực: nhiều tag, script phức tạp, CSS inline, event handler...
   - HTML mock: chỉ ~10 tag, cấu trúc cơ bản = mô hình không recognize

### **Kết Quả:**
- HTML mock được classify sai
- Vì nó không giống HTML trong training dataset

---

## ❌ **VẤN ĐỀ 2: DOM Model (Lines 189-207)**

### **Mock DOM Record (SAI):**
```typescript
const getMockDomRecord = (): object => {
  // Fixed mock DOM record (same every time)
  return {
    nodes: [
      { tag: "html" },
      { tag: "head" },
      { tag: "title", text_len: 11 },
      { tag: "body" },
      { tag: "h1", text_len: 7 },
      { tag: "form" },
      { tag: "input", attrs: { type: "email", is_pw: 0 } },
      { tag: "input", attrs: { type: "password", is_pw: 1 } },  // ← Suspicious!
      { tag: "button", text_len: 5 },
      { tag: "script", attrs: { has_src: 1 } }
    ],
    edges: [[0, 1], [0, 3], [1, 2], [3, 4], [3, 5], [5, 6], [5, 7], [5, 8], [3, 9]],
    label: 0
  };
};
```

### **Tại Sao Sai?** 🔴

1. **DOM cũng là MOCK cố định**, không phải DOM thực
2. **DOM này nhìn "nghi ngờ"** vì có password input:
   - Phishing pages thường có password input
   - Nhưng legitimate pages (Facebook, Gmail...) cũng có
3. **Backend GCN model** được train trên DOM graphs thực:
   - Thực: DOM phức tạp từ React/Vue apps, dynamic nodes...
   - Mock: chỉ ~10 nodes = mô hình classify sai

### **Kết Quả:**
- DOM mock được classify sai (thường → PHISHING vì có password input)
- Hoặc classify sai vì DOM đơn quá không match training data

---

## 🎯 **So Sánh URL vs HTML vs DOM:**

| Mô hình | Input | Loại Input | Kết Quả |
|--------|-------|-----------|--------|
| **URL (RNN)** | `https://www.facebook.com/` | **Thực từ dataset** | ✅ 100% đúng |
| **HTML (Transformer)** | Mock HTML cơ bản | **MOCK fixed** | ❌ Sai |
| **DOM (GCN)** | Mock DOM cơ bản | **MOCK fixed** | ❌ Sai |

---

## 🔧 **GIẢI PHÁP: Cần Lấy HTML + DOM Thực Từ Website**

### **Hiện Tại (SAI):**
```typescript
// Frontend chỉ gửi MOCK data → backend classify sai
const htmlContent = getMockHtmlContent();  // ← Mock cố định
const domRecord = getMockDomRecord();      // ← Mock cố định

await checkHtmlViaBackend(htmlContent);
await checkDomViaBackend(domRecord);
```

### **Cần Làm (ĐÚNG):**
```typescript
// Frontend phải:
// 1. Fetch HTML thực từ URL bằng fetch + DOMParser
// 2. Parse DOM tree thực
// 3. Gửi lên backend

// Pseudo code:
const getHtmlFromUrl = async (url) => {
  const resp = await fetch(url);  // ← Lấy HTML thực
  const html = await resp.text();
  return html;
};

const getDomFromHtml = (html) => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");
  const domGraph = convertDomToDomGraph(doc);  // ← Parse DOM
  return domGraph;
};

// Rồi dùng:
const htmlContent = await getHtmlFromUrl(url);
const domRecord = getDomFromHtml(htmlContent);

await checkHtmlViaBackend(htmlContent);      // HTML thực
await checkDomViaBackend(domRecord);         // DOM thực
```

---

## 📊 **Tại Sao URL Model Đúng?**

```
✅ URL Model:
   - Input: "https://www.facebook.com/"
   - Input này THỰC từ user nhập
   - Backend RNN model được train trên URLs thực
   - Input khớp với training data → kết quả đúng
```

---

## 🚨 **Vấn Đề Lớn Hơn:**

### **Backend có các endpoint:**
- `/api/check_url_fast` → input: URL string
- `/api/check_html` → input: HTML string
- `/api/check_dom` → input: DOM graph object

### **Nhưng Frontend đang:**
- ✅ Gửi URL thực (`https://www.facebook.com/`)
- ❌ Gửi HTML mock (generated cố định)
- ❌ Gửi DOM mock (generated cố định)

### **Mô hình backend được train trên:**
- URL thực từ dataset
- HTML thực từ website
- DOM thực từ trang web

**→ Input không match training data = kết quả sai!**

---

## 🔄 **Flow Hiện Tại (SAI):**

```
User nhập: "https://www.facebook.com/"
         ↓
Frontend checkUrl():
  ✅ Gửi URL thực → /api/check_url_fast
  → Backend: 100% chính xác
         ↓
Frontend analyzeHtmlDom():
  ❌ Gửi HTML MOCK (không phải HTML facebook.com) → /api/check_html
  ❌ Gửi DOM MOCK (không phải DOM facebook.com) → /api/check_dom
  → Backend: Classify sai vì input khác
         ↓
Kết quả: HTML/DOM sai
```

---

## 🔄 **Flow Cần Làm (ĐÚNG):**

```
User nhập: "https://www.facebook.com/"
         ↓
Frontend checkUrl():
  ✅ Gửi URL thực → /api/check_url_fast
  → Backend: 100% chính xác
         ↓
Frontend analyzeHtmlDom():
  ✅ Fetch HTML thực từ url → /api/check_html
  ✅ Parse DOM thực từ HTML → /api/check_dom
  → Backend: Classify chính xác vì input khớp training data
         ↓
Kết quả: HTML/DOM chính xác
```

---

## 📝 **Code Fix (Pseudo):**

```typescript
const analyzeHtmlDom = async () => {
  setIsAnalyzing(true);

  try {
    // ✅ FIX 1: Lấy HTML thực từ URL
    const htmlContent = await fetch(url)
      .then(r => r.text());  // HTML thực

    // ✅ FIX 2: Parse DOM thực từ HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, "text/html");
    const domRecord = convertDomToGraph(doc);  // DOM thực

    // Gửi HTML/DOM thực lên backend
    const [htmlRes, domRes] = await Promise.all([
      checkHtmlViaBackend(htmlContent),   // HTML thực
      checkDomViaBackend(domRecord)       // DOM thực
    ]);

    setHtmlResult(htmlRes);
    setDomResult(domRes);
  } catch (err) {
    setError("Lỗi: " + err.message);
  } finally {
    setIsAnalyzing(false);
  }
};
```

---

## ⚠️ **Lưu Ý CORS:**

```
Frontend: http://localhost:8081
Backend: http://localhost:8000

Nếu fetch HTML từ URL thực (ví dụ: https://facebook.com):
  → CORS error! ❌

Cách fix:
  1. Dùng backend proxy: 
     /api/fetch_url?url=... (backend fetch, rồi trả về)
  2. Hoặc dùng Puppeteer/Selenium backend (render + extract HTML)
```

---

## 📌 **Kết Luận:**

| Thành Phần | Hiện Tại | Cần Làm |
|----------|---------|--------|
| **URL Input** | Thực ✅ | Giữ nguyên ✅ |
| **HTML Input** | Mock ❌ | Lấy thực từ URL |
| **DOM Input** | Mock ❌ | Parse từ HTML thực |
| **Kết Quả URL** | Đúng ✅ | Đúng ✅ |
| **Kết Quả HTML** | Sai ❌ | Sẽ đúng (sau fix) |
| **Kết Quả DOM** | Sai ❌ | Sẽ đúng (sau fix) |

---

## 🎯 **Actionable Steps:**

1. **Tìm endpoint backend** để fetch HTML từ URL
   - Nếu có: `/api/fetch_url?url=...`
   - Nếu không: Cần thêm

2. **Tìm hàm convert DOM** từ HTML string:
   - Backend `models_src/preprocessing.py` có không?

3. **Update Frontend** để:
   - Fetch HTML thực
   - Parse DOM thực  
   - Gửi lên backend

4. **Test lại** với link phishing thực

---

**Tóm lại: HTML/DOM sai vì đang gửi MOCK data, cần gửi HTML/DOM THỰC từ website! 🎯**
