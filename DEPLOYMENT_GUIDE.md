# 🚀 Deployment Guide - Cho Mọi Người Truy Cập

## 📋 **Tóm Tắt Nhanh**

Để mọi người truy cập trang web URL Guardian của bạn, bạn có **3 cách**:

| Cách | Chi Phí | Khó | Tốc Độ Deploy | Tốc Độ Run | Url Public |
|-----|---------|-----|---------------|-----------|----------|
| **Localhost** | Miễn phí | Dễ | 5 phút | Nhanh | Không |
| **VPS (Recommended)** | ~$5-10/tháng | Trung bình | 1-2 giờ | Nhanh | Có ✅ |
| **Heroku/Railway** | Miễn phí (basic) | Dễ | 30 phút | Trung bình | Có ✅ |
| **Docker** | Tuỳ | Khó | 2-3 giờ | Nhanh | Có ✅ |

---

## **Option 1: Localhost (Chỉ bạn sử dụng)**

### **Cách làm:**
```powershell
# Terminal 1: Start Backend
cd backend
python main.py
# Output: Running on http://0.0.0.0:8002

# Terminal 2: Start Frontend
npm run dev
# Output: http://localhost:8080
```

### **Truy cập:**
- Từ máy bạn: `http://localhost:8080`
- Từ máy khác trong mạng: `http://<YOUR_PC_IP>:8080` 

**Ưu điểm:** 
- ✅ Nhanh, không cần cấu hình
- ✅ Miễn phí

**Nhược điểm:** 
- ❌ Chỉ khi máy bạn chạy
- ❌ Máy khác không truy cập được (nếu không cùng mạng LAN)

---

## **Option 2: VPS (Đề Xuất ⭐)**

### **Bước 1: Chọn VPS Provider**

**Gợi ý:**
- **DigitalOcean** ($6/tháng, dễ dùng)
- **Linode** ($5/tháng, stable)
- **AWS EC2** (free tier, rồi $0.01-5/tháng)
- **Vultr** ($6/tháng, nhanh)

### **Bước 2: Tạo VPS Server**

Ví dụ với DigitalOcean:

1. Tạo Droplet: Ubuntu 22.04 LTS
2. Chọn $6/tháng (1GB RAM, 1 CPU, 25GB SSD)
3. Kích "Create"
4. SSH vào: `ssh root@<YOUR_VPS_IP>`

### **Bước 3: Setup VPS**

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python & Node
sudo apt install -y python3.11 python3-pip nodejs npm git curl

# 3. Install PM2 (để keep app chạy 24/7)
sudo npm install -g pm2

# 4. Clone project
git clone https://github.com/<YOUR_REPO>/url-guardian.git
cd url-guardian

# 5. Install dependencies
pip install -r backend/requirements.txt
npm install

# 6. Build frontend
npm run build
# Output: dist/ folder (production build)
```

### **Bước 4: Cấu Hình Nginx (Reverse Proxy)**

```bash
# Install Nginx
sudo apt install -y nginx

# Create config file
sudo nano /etc/nginx/sites-available/url-guardian
```

Paste vào:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Thay bằng domain của bạn
    
    # Frontend (React)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
}
```

```bash
# Enable config
sudo ln -s /etc/nginx/sites-available/url-guardian /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **Bước 5: Start Apps với PM2**

```bash
# Start backend
pm2 start "python backend/main.py" --name "url-guardian-backend"

# Start frontend (production)
pm2 start "npm run preview" --name "url-guardian-frontend"

# Save PM2 config
pm2 startup
pm2 save

# Monitor
pm2 monit
pm2 logs
```

### **Bước 6: Setup SSL (HTTPS)**

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (miễn phí)
sudo certbot --nginx -d your-domain.com

# Auto-renew
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### **Kết Quả:**
```
✅ https://your-domain.com → Accessible từ toàn bộ internet
✅ Backend chạy 24/7
✅ Frontend tự động restart nếu crash
✅ HTTPS/SSL bảo mật
```

---

## **Option 3: Heroku/Railway (Nhanh Nhất)**

### **Deploy lên Railway.app (Dễ & Miễn Phí)**

#### **Bước 1: Chuẩn bị**

Tạo file `Procfile` trong root directory:
```
web: npm run build && npm run preview
worker: python backend/main.py
```

Tạo file `runtime.txt`:
```
python-3.11.5
```

#### **Bước 2: Deploy**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

#### **Kết Quả:**
- Backend: `https://url-guardian-backend.railway.app`
- Frontend: `https://url-guardian-frontend.railway.app`

**Ưu điểm:**
- ✅ Miễn phí + dễ
- ✅ Auto-scaling
- ✅ HTTPS tự động

**Nhược điểm:**
- ❌ Tốc độ chậm hơn VPS
- ❌ Có giới hạn resource

---

## **Option 4: Docker (Professional)**

### **Bước 1: Tạo Dockerfile**

`Dockerfile` (backend):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY CKPT/ ../CKPT/

EXPOSE 8002

CMD ["python", "main.py"]
```

`Dockerfile.frontend` (frontend):
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package.json package-lock.json .
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist dist

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]
```

### **Bước 2: Docker Compose**

`docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8002:8002"
    environment:
      - API_PORT=8002
    volumes:
      - ./CKPT:/app/CKPT

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8002

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
```

### **Bước 3: Deploy**

```bash
# Khởi chạy toàn bộ
docker-compose up -d

# Monitor
docker-compose logs -f
```

---

## 🎯 **Recommend Setup cho Bạn**

### **Phase 1: Immediate (Bây giờ)**
```
1. Keep running locally → Show people from your PC IP
   - Máy bạn phải bật 24/7
   - Url: http://<YOUR_PC_IP>:8080
```

### **Phase 2: Short-term (1-2 tuần)**
```
1. Deploy lên Railway.app (miễn phí, dễ)
   - Public URL: https://url-guardian.railway.app
   - Mọi người có thể truy cập
```

### **Phase 3: Long-term (Production)**
```
1. Chọn VPS ($6/tháng) + Nginx + SSL
   - Your own domain: https://your-domain.com
   - Professional, fast, reliable
```

---

## 📊 **So Sánh Chi Tiết**

| Feature | Localhost | VPS | Railway | Docker |
|---------|-----------|-----|---------|--------|
| **Public Access** | ❌ | ✅ | ✅ | ✅ |
| **Cost** | Free | $5-10/mo | Free-$5 | Free |
| **Uptime** | 99% (máy bạn) | 99.9% | 99% | 99.9% |
| **Speed** | Nhanh | Nhanh | Chậm | Nhanh |
| **Maintenance** | Dễ | Trung bình | Dễ | Khó |
| **Setup Time** | 5 phút | 1-2 giờ | 30 phút | 2-3 giờ |
| **SSL/HTTPS** | ❌ | ✅ | ✅ | ✅ |
| **Auto-scaling** | ❌ | ❌ | ✅ | ✅ |
| **Domain** | No | Yes | Yes | Yes |

---

## 🔧 **Troubleshooting**

### **Problem: Frontend không connect được Backend**

**Nguyên nhân:** CORS hoặc API URL sai

**Fix:**
```tsx
// src/pages/Index.tsx
// Change từ:
const response = await fetch("http://localhost:8002/api/analyze_url_full", ...)

// Thành (nếu deployed):
const response = await fetch("https://your-domain.com/api/analyze_url_full", ...)
```

### **Problem: Models loading lâu**

**Nguyên nhân:** First load bắt buộc phải load checkpoint

**Fix:**
- Gán thêm RAM
- Optimize models (quantization)
- Load models cached

### **Problem: Port conflict**

**Fix:**
```bash
# Change backend port
export API_PORT=8080
python backend/main.py

# Change frontend port
npm run dev -- --port 5173
```

---

## 📝 **Checklist Trước Deploy**

- [ ] Test backend: `curl http://localhost:8002/health`
- [ ] Test frontend: Visit `http://localhost:8080`
- [ ] Update API URLs trong code
- [ ] Check requirements.txt → Có tất cả packages?
- [ ] Check package.json → Có tất cả dependencies?
- [ ] Test trên production build: `npm run build && npm run preview`
- [ ] Prepare domain name (nếu dùng VPS)
- [ ] Backup code vào Git
- [ ] Document deployment steps

---

## 🚀 **Quick Start: Deploy lên Railway (30 phút)**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Create Procfile
echo "web: npm run build && npm run preview" > Procfile
echo "worker: python backend/main.py" >> Procfile

# 4. Deploy
railway up

# 5. Check logs
railway logs

# Output:
# 🎉 Deployed at: https://url-guardian.railway.app
```

---

## ❓ **FAQ**

### Q: Tôi có thể để máy tính chạy 24/7 không?

**A:** Có nhưng không khuyến khích. Tốn điện, heat, fan noise. VPS rẻ hơn (~$6/tháng).

### Q: Miền tên bao nhiêu tiền?

**A:** $10-15/năm (Namecheap, GoDaddy).

### Q: Mô hình có thể run trên CPU không?

**A:** Có, nhưng chậm (50-200ms → 200-500ms). VPS CPU enough.

### Q: Cần database không?

**A:** Hiện tại chỉ lưu history trong localStorage. Nếu muốn persistent, thêm PostgreSQL ($7/tháng).

### Q: Có thể tăng tốc độ không?

**A:** Có:
- CDN (Cloudflare free)
- Model quantization
- Caching improvements
- Database optimization

