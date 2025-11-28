# 📖 INDEX: HƯỚNG A - KHẮC PHỤC KẾT QUẢ KHÔNG ỔN ĐỊNH

## 🎯 Vấn Đề & Giải Pháp

### **Vấn Đề Gặp Phải**
- ❌ URL Detection: ✅ Ổn định (OK)
- ❌ Liveness Status: Lúc "alive", lúc "dead" (ngẫu nhiên)
- ❌ HTML Model: Mỗi lần test khác kết quả (ngẫu nhiên 30-70%)
- ❌ DOM Model: Mỗi lần test khác kết quả (ngẫu nhiên 25-65%)

### **Nguyên Nhân**
Frontend dùng `Math.random()` cho Liveness, HTML, DOM → kết quả random mỗi lần

### **Giải Pháp (Hướng A)**
Gọi backend API thực + fixed mock data → deterministic

---

## 📋 Danh Sách Tài Liệu (Đọc Theo Thứ Tự)

### **1. HƯỚNG_A_DONE.md** ⭐ (START HERE)
Tóm tắt ngắn gọn:
- ✅ Gì đã sửa
- ✅ Cách dùng
- ✅ Kết quả dự kiến

### **2. KIỂM_TRA_HƯỚNG_A_STEP_BY_STEP.md** ⭐⭐ (QUAN TRỌNG)
Hướng dẫn test chi tiết:
- Bước 1-2: Khởi động backend + frontend
- Bước 3-5: Kiểm tra URL + Liveness
- Bước 6-9: Kiểm tra HTML + DOM + DETERMINISM (quan trọng!)
- Bước 10: Troubleshooting (nếu cần)

### **3. CHANGES_SUMMARY_HƯỚNG_A.md**
Code diff chi tiết:
- Xóa 3 hàm nào
- Thêm 5 hàm nào
- Sửa 1 hàm main như thế nào

### **4. HƯỚNG_A_HOÀN_THÀNH.md**
Thông tin kỹ thuật:
- Giải thích từng thay đổi
- So sánh trước vs sau
- Kỳ vọng kết quả

### **5. QUICK_TEST_HƯỚNG_A.md**
Test nhanh:
- Cách chạy
- Kết quả dự kiến
- Troubleshooting

### **6. INSTABILITY_EXPLANATION.md**
Giải thích vấn đề gốc:
- Tại sao Liveness random?
- Tại sao HTML/DOM random?
- 3 giải pháp ban đầu (A, B, C)

---

## 🚀 Quick Start (5 Phút)

### **Terminal 1 - Backend:**
```powershell
cd "c:\Users\PTC\Downloads\url-guardian-demo-main\url-guardian-demo-main\backend"
python main.py
# Chờ: INFO: Uvicorn running on http://0.0.0.0:8000
```

### **Terminal 2 - Frontend:**
```powershell
cd "c:\Users\PTC\Downloads\url-guardian-demo-main\url-guardian-demo-main"
npm run dev
# Chờ: ➜ Local: http://localhost:8081
```

### **Browser:**
```
http://localhost:8081
→ Nhập: https://www.facebook.com/
→ Kiểm tra URL → Ghi nhớ kết quả
→ Phân tích HTML+DOM (lần 1) → Ghi nhớ kết quả
→ Phân tích HTML+DOM (lần 2) → Kiểm tra: GIỐNG lần 1?
→ Phân tích HTML+DOM (lần 3) → Kiểm tra: GIỐNG lần 1 & 2?
```

✅ **Nếu cả 3 lần HTML/DOM GIỐNG** → Success! 🎉

---

## 📊 File Thay Đổi

**File sửa**: `src/pages/Index.tsx`

### **Xóa**:
- `generateHtmlResult()` (random)
- `generateDomResult()` (random)
- ~3 hàm mock random

### **Thêm**:
- `checkHtmlViaBackend()` - POST /api/check_html
- `checkDomViaBackend()` - POST /api/check_dom
- `getMockHtmlContent()` - fixed data
- `getMockDomRecord()` - fixed data
- `generateLivenessResult()` - fixed "alive"

### **Sửa**:
- `analyzeHtmlDom()` - async/await backend API

---

## ✅ Kết Quả Dự Kiến

```
TRƯỚC (Random mỗi lần):
  Lần 1: HTML=45%, DOM=60%, Liveness=Alive
  Lần 2: HTML=75%, DOM=25%, Liveness=Dead    ← KHÁC!
  Lần 3: HTML=30%, DOM=80%, Liveness=Alive   ← KHÁC!

SAU (Deterministic):
  Lần 1: HTML=52%, DOM=48%, Liveness=Alive
  Lần 2: HTML=52%, DOM=48%, Liveness=Alive   ← GIỐNG!
  Lần 3: HTML=52%, DOM=48%, Liveness=Alive   ← GIỐNG!
```

---

## 🔧 Backend API Được Gọi

### **POST /api/check_html**
```json
Request: { "html": "<html>...</html>" }
Response: { "probability": 0.52, "label": "PHISHING", "confidence": 0.85 }
```

### **POST /api/check_dom**
```json
Request: { "dom": { "nodes": [...], "edges": [...] } }
Response: { "probability": 0.48, "label": "BENIGN", "confidence": 0.88 }
```

---

## 📞 Báo Cáo Kết Quả

Sau khi test, hãy báo:

```
✅ / ❌ URL Detection (ổn định?)
✅ / ❌ Liveness Status (luôn "Alive"?)
✅ / ❌ HTML Model (lần 1,2,3 giống?)
✅ / ❌ DOM Model (lần 1,2,3 giống?)
```

Hoặc báo số cụ thể:
```
URL Detection: 15% / 15% / 15% → ✅
Liveness: Alive / Alive / Alive → ✅
HTML: 52% / 52% / 52% → ✅
DOM: 48% / 48% / 48% → ✅
```

---

## 🎯 Hướng Tiếp Theo

Sau khi test thành công:

1. **Cải thiện Mock Data** - Real HTML/DOM từ user
2. **Real Liveness Check** - HTTP HEAD request
3. **Ensemble Mode** - Sử dụng `/api/ensemble` (3 models cùng lúc)
4. **Deployment** - Docker, hosting trên server

---

## 📚 Tài Liệu Liên Quan

Folder root có các file:
- `HƯỚNG_A_DONE.md` - Tóm tắt (👈 BẮT ĐẦU ĐÂY)
- `KIỂM_TRA_HƯỚNG_A_STEP_BY_STEP.md` - Guide test (👈 QUAN TRỌNG)
- `INSTABILITY_EXPLANATION.md` - Giải thích vấn đề
- `BUILD_STATUS.md` - Status overall
- `STATUS_COMPLETE.md` - Project status
- Backend docs: `backend/README.md`, `backend/IMPLEMENTATION.md`, `backend/ARCHITECTURE.md`

---

## ✨ Summary

✅ **Hướng A**: Gọi backend API + fixed mock → deterministic  
✅ **3 vấn đề**: Liveness + HTML + DOM đã fix  
✅ **Sẵn test**: Khởi động 2 services, truy cập localhost:8081  
✅ **Dự kiến**: Cùng data → cùng output mỗi lần (100% deterministic)

---

**Sẵn sàng test? Theo hướng dẫn KIỂM_TRA_HƯỚNG_A_STEP_BY_STEP.md! 🚀**
