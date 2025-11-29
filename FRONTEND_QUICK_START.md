# 🚀 How to Run the Frontend

This guide shows you how to start the URL Guardian frontend application.

## ✅ Prerequisites

- ✓ **Node.js** v18+ (you have v22.16.0)
- ✓ **npm** v8+ (you have v10.9.2)
- ✓ **Backend running** on http://localhost:8002

## 📋 Step-by-Step Setup

### Step 1: Install Dependencies

Navigate to the frontend directory and install all required packages:

```bash
cd frontend
npm install
```

This will:
- Download all npm packages listed in `package.json`
- Create `node_modules/` directory
- Generate `package-lock.json` for reproducible installs

**Time**: ~2-5 minutes depending on internet speed

### Step 2: Start Development Server

```bash
npm run dev
```

You should see output like:

```
➜  Local:   http://localhost:8080/
➜  press h + enter to show help
```

### Step 3: Open in Browser

Open your browser and navigate to:

```
http://localhost:8080
```

The app should load with:
- 🔗 URL Guardian header
- 📝 Two tabs: "Check URL" and "Upload HTML"
- 📋 Recent Checks sidebar
- 🌙 Dark mode toggle

## 🎯 Common Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start development server (with hot reload) |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Check code quality |

## ⚙️ Configuration

### Change Backend URL

If your backend is running on a different URL, set the environment variable:

**Windows (PowerShell):**
```powershell
$env:VITE_API_URL="http://your-backend-url:8002"
npm run dev
```

**Windows (CMD):**
```cmd
set VITE_API_URL=http://your-backend-url:8002
npm run dev
```

**Or create `.env` file in `frontend/` directory:**
```
VITE_API_URL=http://your-backend-url:8002
```

### Change Development Port

To use a different port (e.g., 3000):

```bash
npm run dev -- --port 3000
```

Then access: `http://localhost:3000`

## 🧪 Testing the App

### 1. Check the URL Analysis

1. Go to **Check URL** tab
2. Enter a URL: `https://google.com`
3. Click **Check** or press **Enter**
4. Wait for results from all 3 models

### 2. Upload HTML

1. Go to **Upload HTML** tab
2. Create a simple HTML file or use an existing one
3. Upload and analyze

### 3. View History

- Recent checks appear in the **Recent Checks** sidebar
- Click ↻ to re-check any URL
- History persists in browser local storage

### 4. Try Dark Mode

- Click the 🌙 button in the top-right
- Your preference is saved

## 📦 Production Deployment

### Build for Production

```bash
npm run build
```

This creates a `dist/` folder with optimized files.

### Preview Production Build

```bash
npm run preview
```

This serves the production build locally to test before deployment.

## 🐛 Troubleshooting

### Issue: "Cannot find module" errors

**Solution**: Clear and reinstall dependencies

```bash
rm -r node_modules package-lock.json
npm install
```

### Issue: Port 8080 already in use

**Solution**: Use a different port

```bash
npm run dev -- --port 3000
```

### Issue: Backend connection fails

**Solution**: 

1. Check backend is running:
   ```bash
   curl http://localhost:8002/health
   ```

2. If not running, start it:
   ```bash
   cd backend
   python main.py
   ```

3. If using a remote backend, set `VITE_API_URL` environment variable

### Issue: Slow performance

**Solution**:

1. Clear browser cache
2. Close unnecessary browser tabs
3. Restart development server: Press `Ctrl+C`, then `npm run dev`

## 📚 Useful Resources

- **Vite Documentation**: https://vitejs.dev
- **React Documentation**: https://react.dev
- **TypeScript Documentation**: https://www.typescriptlang.org
- **Tailwind CSS**: https://tailwindcss.com
- **shadcn/ui Components**: https://ui.shadcn.com

## 🔗 Next Steps

1. ✅ Run `npm install` to install dependencies
2. ✅ Ensure backend is running on port 8002
3. ✅ Run `npm run dev` to start the app
4. ✅ Open http://localhost:8080 in your browser
5. ✅ Test with sample URLs or HTML files

## 💡 Tips

- Use keyboard shortcut **Enter** to quickly submit URL analysis
- Results can be **copied** or **exported** as JSON
- **History** is stored locally and won't be cleared unless you clear browser data
- For development, keep the dev server running and just save changes - they hot-reload automatically

---

**Happy phishing detecting! 🎣🔒**
