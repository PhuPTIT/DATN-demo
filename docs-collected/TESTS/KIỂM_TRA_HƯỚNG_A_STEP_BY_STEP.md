# 🚀 HƯỚNG DẪN KIỂM TRA HƯỚNG A (STEP-BY-STEP)

## 📍 Bước 1: Khởi Động Backend (nếu chưa chạy)

**Terminal 1** - Mở PowerShell mới:
```powershell
cd "c:\Users\PTC\Downloads\url-guardian-demo-main\url-guardian-demo-main\backend"
python main.py
```

**Mong đợi Output:**
```
[INFO] Using device: cpu
[INFO] Loading models...
[OK] URL model (RNN) loaded
[OK] HTML model (Transformer) loaded
[OK] DOM model (GCN) loaded
[OK] Ensemble predictor created
[START] Starting server on 0.0.0.0:8000
[INFO] API docs available at http://localhost:8000/docs
INFO:     Started server process [12345]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **Nếu thấy vậy**: Backend ready! Giữ terminal này mở.
❌ **Nếu lỗi**: Kiểm tra backend chưa được stop từ lần trước (bấm `Ctrl+C` 1 lần rồi chạy lại).

---

## 📍 Bước 2: Khởi Động Frontend (nếu chưa chạy)

**Terminal 2** - Mở PowerShell mới:
```powershell
cd "c:\Users\PTC\Downloads\url-guardian-demo-main\url-guardian-demo-main"
npm run dev
```

**Mong đợi Output:**
```
  VITE v5.4.19  ready in 300 ms

  ➜  Local:   http://localhost:8081/
  ➜  Network: http://172.19.163.222:8081/
  ➜  press h + enter to show help
```

✅ **Nếu thấy vậy**: Frontend ready!
❌ **Nếu lỗi**: Kiểm tra port 8080/8081 có bị chiếm không (nếu cần đổi port, check lại Vite logs).

---

## 📍 Bước 3: Mở Website

**Browser** - Gõ URL:
```
http://localhost:8081
```

**Mong đợi:** Thấy trang "Phishing URL Checker" với input field + buttons.

✅ **Nếu thấy giao diện**: Tiếp bước 4.
❌ **Nếu không load**: Kiểm tra Terminal 2 (frontend) có lỗi không, hoặc hard refresh (Ctrl+Shift+R).

---

## 📍 Bước 4: Kiểm Tra URL Detection (Baseline - nên ổn định từ trước)

1. **Nhập URL:**
   ```
   https://www.facebook.com/
   ```

2. **Bấm nút:** "Kiểm tra URL"

3. **Quan sát kết quả:**
   - Label: Phishing hoặc Benign
   - Probability: % nào đó (ví dụ: 15%)
   - Reasons: Danh sách các lý do

4. **Ghi nhớ số %**: Ví dụ **15% Benign**

✅ **Kết quả URL nên ổn định** (nếu kiểm tra 3 lần, nên thấy cùng 15%).

---

## 📍 Bước 5: Kiểm Tra Liveness Status (mới sửa - nên luôn "Alive")

**Quan sát kbox "Trạng thái URL (Liveness)" bên phải URL result:**

**Mong đợi:**
- Status: `Còn hoạt động` (không phải "Không truy cập được")
- Message: "URL có khả năng truy cập (chưa verify thực)"

✅ **Nếu luôn "Còn hoạt động"**: Correct! Liveness giờ fixed, không random.
❌ **Nếu vẫn thay đổi (lúc alive, lúc dead)**: Có thể browser cache cũ → `Ctrl+Shift+R` hard refresh.

---

## 📍 Bước 6: Kiểm Tra HTML Model (mới sửa - GỌI BACKEND API)

1. **Bấm nút:** "Phân tích HTML + DOM"

2. **Chờ loading:** 2-3 giây (gọi backend API)

3. **Quan sát kBox "Kết quả mô hình HTML":**
   - Label: Phishing hoặc Benign
   - Probability: % nào đó (ví dụ: **52%**)
   - Model: "Transformer (byte-level)"

4. **Ghi nhớ % HTML**: Ví dụ **52% Phishing**

✅ **Nếu thấy từ 52%**: Backend API call thành công!

---

## 📍 Bước 7: Kiểm Tra DOM Model (mới sửa - GỌI BACKEND API)

**Quan sát kBox "Kết quả mô hình DOM" (bên cạnh HTML):**
- Label: Phishing hoặc Benign
- Probability: % nào đó (ví dụ: **48%**)
- Model: "Graph Convolutional Network (GCN)"

✅ **Ghi nhớ % DOM**: Ví dụ **48% Benign**

---

## 📍 Bước 8: TEST DETERMINISM - Lần Kiểm Tra 2

**Bấm lại nút:** "Phân tích HTML + DOM"

**Chờ 2-3 giây rồi quan sát:**

```
Lần 1 (Bước 6-7):
  HTML: 52% Phishing
  DOM: 48% Benign

Lần 2 (Bây giờ):
  HTML: ??? %
  DOM: ??? %
```

✅ **NẾU GIỐNG**: HTML = 52%, DOM = 48% → **DETERMINISTIC! ✅**
❌ **NẾU KHÁC**: → Có vấn đề, tiếp bước 9.

---

## 📍 Bước 9: TEST DETERMINISM - Lần Kiểm Tra 3

**Bấm lại nút:** "Phân tích HTML + DOM" lần 3

**Quan sát:**
```
Lần 1:
  HTML: 52% Phishing
  DOM: 48% Benign

Lần 2:
  HTML: 52% Phishing
  DOM: 48% Benign

Lần 3 (Bây giờ):
  HTML: ??? %
  DOM: ??? %
```

✅ **NẾU CẢ 3 LẦN GIỐNG**: **HƯỚNG A THÀNH CÔNG! 🎉**
❌ **NẾU VẪN KHÁC**: → Troubleshooting (Bước 10).

---

## 📍 Bước 10: Troubleshooting (nếu cần)

### **A. Browser Console - Kiểm Tra Lỗi**

Bấm `F12` → Tab "Console":

```javascript
// Tìm lỗi như:
ERROR: Unable to connect to the remote server
ERROR: fetch failed
```

**Giải pháp:**
- Backend chưa chạy hoặc crash
- Restart backend (Terminal 1: `Ctrl+C` → `python main.py` lại)

### **B. Browser Network Tab - Kiểm Tra API Call**

Bấm `F12` → Tab "Network":

- Bấm "Phân tích HTML + DOM"
- Tìm request `check_html` và `check_dom`
- Xem status: **200** (success) hay **400/500** (error)?

**Nếu 200**: Backend nhận request OK
**Nếu 400/500**: Lỗi backend, check Terminal 1 logs

### **C. Backend Log - Kiểm Tra Server**

**Mở Terminal 1** (backend running), xem log:

```
INFO:     127.0.0.1:65432 - "POST /api/check_html HTTP/1.1" 200 OK
INFO:     127.0.0.1:65433 - "POST /api/check_dom HTTP/1.1" 200 OK
```

✅ Nếu thấy 200: OK
❌ Nếu thấy 500: Có lỗi backend

### **D. Hard Refresh Browser**

Bấm: `Ctrl+Shift+R` (force clear cache)

Sau đó test lại Bước 6-9.

---

## 📊 BẢNG TÓMLẠI KẾT QUẢ MONG ĐỢI

| Phần | Lần 1 | Lần 2 | Lần 3 | Trạng Thái |
|------|-------|-------|-------|-----------|
| **URL** | 15% Benign | 15% Benign | 15% Benign | ✅ Ổn định |
| **Liveness** | Alive | Alive | Alive | ✅ Ổn định |
| **HTML** | 52% Phishing | 52% Phishing | 52% Phishing | ✅ Ổn định (sửa xong) |
| **DOM** | 48% Benign | 48% Benign | 48% Benign | ✅ Ổn định (sửa xong) |

---

## 🎉 KẾT LUẬN

✅ **Nếu tất cả 3 lần HTML/DOM là số nhất quán** → **HƯỚNG A THÀNH CÔNG!**

🎊 **Kết quả không còn random, hoàn toàn deterministic từ backend model!**

---

## 📞 Báo Cáo Kết Quả

Sau khi test xong, hãy cho biết:

```
URL Detection (Lần 1, 2, 3): ??? % 
Liveness Status (Lần 1, 2, 3): ??? / ??? / ???
HTML Model (Lần 1, 2, 3): ??? % / ??? % / ??? %
DOM Model (Lần 1, 2, 3): ??? % / ??? % / ??? %
```

Ví dụ:
```
URL Detection: 15% / 15% / 15% ✅
Liveness: Alive / Alive / Alive ✅
HTML Model: 52% / 52% / 52% ✅
DOM Model: 48% / 48% / 48% ✅
```

Nếu thấy tất cả ổn định → **Hướng A hoàn thành thành công! 🚀**
