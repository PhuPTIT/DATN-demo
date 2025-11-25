# 🔧 TEMPORARY WORKAROUND: Backend Port Conflict

## Vấn Đề
- Port 8000 bị chiếm dụng
- Backend chạy trên port **8001** thay vì **8000**
- Frontend vẫn gọi localhost:**8000** → kết quả lỗi "Cannot fetch HTML"

## Giải Pháp Tạm Thời

### **Option 1: Cập nhật Frontend URL** (Quick Fix)
Muốn tôi update tất cả `localhost:8000` thành `localhost:8001` trong frontend code không?

```typescript
// Change ALL instances of:
fetch("http://localhost:8000/api/...

// To:
fetch("http://localhost:8001/api/...
```

### **Option 2: Restart toàn bộ system**
```powershell
# Restart computer để free up port 8000
# Rồi start lại backend
```

### **Option 3: Find & kill process using port 8000**
```powershell
netstat -ano | findstr ":8000"
taskkill /PID <PID> /F
```

---

## ✅ Current Status

- ✅ **Backend**: Running on `http://localhost:8001`
- ✅ **Frontend**: Running on `http://localhost:8082` 
- ✅ **Endpoint `/api/fetch_url_resources`**: WORKING! ✅
  - Test: Fetched Google.com HTML (273KB)
  
```
curl -X POST "http://localhost:8001/api/fetch_url_resources" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.google.com/"}'

Response: ✅ 273KB HTML received
```

---

## 🎯 Recommend: Option 1

Hãy cho tôi update Frontend để gọi **port 8001** thay vì 8000?

---

## 📝 Tất cả URLs cần update:

```typescript
// File: src/pages/Index.tsx

Line 112:   http://localhost:8000/api/check_html
Line 145:   http://localhost:8000/api/check_dom
Line 182:   http://localhost:8000/api/fetch_url_resources
Line 322:   http://localhost:8000/api/check_url_fast

// Thay thành:
Line 112:   http://localhost:8001/api/check_html
Line 145:   http://localhost:8001/api/check_dom
Line 182:   http://localhost:8001/api/fetch_url_resources
Line 322:   http://localhost:8001/api/check_url_fast
```

---

## ❓ Nguyên Nhân

Port 8000 có process khác đang dùng (có thể từ session backend cũ chưa fully kill).
Khi khởi động backend, nó chạy trên port sẵn có tiếp theo là 8001.

---

**Bạn muốn tôi:**
1. ✅ Update Frontend để gọi port 8001?
2. ❌ Hoặc restart và giải quyết port 8000?

Lựa chọn nào bạn muốn?
