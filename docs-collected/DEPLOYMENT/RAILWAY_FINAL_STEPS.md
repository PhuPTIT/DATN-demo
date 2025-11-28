# 🚀 DEPLOY LÊN RAILWAY - FINAL STEPS

## **✅ Current Status:**
- ✅ Git installed
- ✅ Code pushed to GitHub: https://github.com/PhuPTIT/DATN-demo
- ✅ All 176 files uploaded (70MB)
- ✅ Deployment files created (Procfile, runtime.txt, .railwayignore)

---

## **🎯 Next: Deploy Lên Railway**

### **Bước 1: Tạo tài khoản Railway**

1. Vào: https://railway.app
2. Click **"Sign Up"**
3. Chọn: **Continue with GitHub**
4. Authorize Railway

### **Bước 2: Create New Project**

1. Click **"New Project"**
2. Chọn **"Deploy from GitHub"**
3. Click **"Connect Repository"**

### **Bước 3: Select Repository**

1. Chọn repo: **PhuPTIT/DATN-demo**
2. Click **"Deploy"**

### **Bước 4: Configure & Deploy**

Railway sẽ tự động:
- ✅ Detect Procfile
- ✅ Install Python 3.11
- ✅ Install Node.js dependencies
- ✅ Build React frontend
- ✅ Start FastAPI backend
- ✅ Assign public URL

### **Expected Result (3-5 minutes):**

```
✅ Frontend:  https://datn-demo-XXXXX.railway.app
✅ Backend:   /api/* endpoints
✅ Models:    All 3 models loaded
✅ Public URL: Everyone can access!
```

---

## **📝 Setup Environment Variables (Important)**

In Railway Dashboard:
1. Click **Variables**
2. Add:
   ```
   VITE_API_URL=https://datn-demo-XXXXX.railway.app
   PYTHONUNBUFFERED=1
   NODE_ENV=production
   ```
3. Click **"Save"** → Auto-redeploy

---

## **✅ After Deploy: Test**

1. Open: https://datn-demo-XXXXX.railway.app
2. Enter URL: `https://paypal-verify.tk`
3. Click Analyze
4. Should see all 3 models results + Ensemble verdict

---

## **💡 Tips**

- **Logs:** Click Deployments → View Logs
- **Restart:** Settings → Redeploy
- **Custom Domain:** Networking → Add Domain
- **SSL:** Automatic (free)
- **Monitor:** Real-time logs & metrics

---

**Go to https://railway.app and let's deploy!** 🚀

