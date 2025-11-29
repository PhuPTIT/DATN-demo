# 🔗 URL Guardian Frontend

A modern, responsive web application for phishing URL detection using an ensemble of 3 deep learning AI models. Built with React, TypeScript, Vite, Tailwind CSS, and shadcn/ui components.

## 🎯 Features

- **🚀 Fast Analysis**: Real-time phishing detection with multiple AI models
- **📊 Detailed Results**: View predictions from URL, HTML, and DOM models
- **📋 History Tracking**: Automatically saves recent checks to local storage
- **🌙 Dark Mode**: Toggle between light and dark themes
- **📥 HTML Upload**: Upload and analyze HTML files directly
- **💾 Export Results**: Download analysis results as JSON
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **🎨 Modern UI**: Built with shadcn/ui components and Tailwind CSS
- **⌨️ Keyboard Support**: Press Enter to submit URL analysis

## 🏗️ Architecture

### Tech Stack

- **Frontend Framework**: React 18.3
- **Language**: TypeScript 5.8
- **Build Tool**: Vite 5.4
- **Styling**: Tailwind CSS 3.4
- **UI Components**: shadcn/ui
- **Routing**: React Router v6
- **State Management**: React Query (TanStack Query)
- **Form Handling**: React Hook Form + Zod validation
- **Icons**: Lucide React

### Component Structure

```
src/
├── App.tsx                     # Main app wrapper with providers
├── main.tsx                    # Entry point
├── pages/
│   ├── Index.tsx              # Main analysis page
│   ├── IndexNew.tsx           # (Alternative layout)
│   └── NotFound.tsx           # 404 page
├── components/
│   ├── NavLink.tsx            # Custom nav link component
│   └── ui/                    # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── tabs.tsx
│       ├── toast.tsx
│       └── ...50+ other UI components
├── hooks/
│   ├── use-mobile.tsx         # Responsive mobile detection
│   └── use-toast.ts           # Toast notifications
└── lib/
    └── utils.ts               # Utility functions

```

## 📋 Prerequisites

- **Node.js**: v18+ (includes npm)
- **Bun** (optional): v1.0+ for faster package management
- **Backend**: Running on `http://localhost:8002` (or configured via `VITE_API_URL`)

## 🚀 Quick Start

### 1️⃣ Install Dependencies

Using npm:
```bash
cd frontend
npm install
```

Using bun (faster):
```bash
cd frontend
bun install
```

### 2️⃣ Start Development Server

Using npm:
```bash
npm run dev
```

Using bun:
```bash
bun run dev
```

The app will start on **http://localhost:8080** by default (configured in `vite.config.ts`).

### 3️⃣ Open in Browser

Navigate to:
```
http://localhost:8080
```

## 📝 Usage

### Check URL for Phishing

1. Go to the **Check URL** tab
2. Enter a URL (e.g., `https://example.com`)
3. Click **Check** or press **Enter**
4. View results from all 3 models and the ensemble verdict
5. See confidence levels and explanations

### Upload HTML File

1. Go to the **Upload HTML** tab
2. Click or drag-and-drop an HTML file
3. Click **Analyze HTML**
4. View the analysis results

### View History

- Recent checks are displayed in the right sidebar
- Click the ↻ icon to re-check a URL
- History is persisted to browser local storage

### Export Results

- Click **Copy** to copy the JSON result to clipboard
- Click **Export** to download as `phishing-analysis.json`
- Click **Clear** to reset the current analysis

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Backend API URL (default: http://localhost:8002)
VITE_API_URL=http://localhost:8002

# Mode (development or production)
VITE_MODE=development
```

### Vite Configuration

Edit `vite.config.ts` to customize:

```typescript
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",        // Listen on all interfaces
    port: 8080,        // Development server port
  },
  plugins: [react(), mode === "development" && componentTagger()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),  // Path alias
    },
  },
}));
```

### Tailwind Configuration

Customize theme in `tailwind.config.ts`:

```typescript
export const config: Config = {
  darkMode: ["class"],
  theme: {
    extend: {
      // Your custom theme extensions
    },
  },
};
```

## 🏗️ Build & Deployment

### Development Build

```bash
npm run dev
```

Starts a local development server with hot reload.

### Production Build

```bash
npm run build
```

Outputs optimized production build to `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

Preview the production build locally before deployment.

### Build with Development Mode

```bash
npm run build:dev
```

Production build with development settings (useful for debugging).

## 📦 Available Scripts

```bash
# Development server (with hot reload)
npm run dev

# Production build only
npm run build

# Production build (dev mode - for debugging)
npm run build:dev

# Build + Run from dist folder (recommended for production)
npm run build:prod

# Preview production build from dist folder
npm run preview

# Lint code
npm run lint
```

**Quick Commands with Bun (faster):**
```bash
# Using Bun instead of npm (2x faster)
bun run dev
bun run build:prod
bun run preview
```

## 🔌 API Integration

The frontend communicates with the backend via these endpoints:

### POST `/api/analyze_url_full`
Comprehensive URL analysis with all 3 models

**Request:**
```json
{
  "url": "https://example.com",
  "normalize": true
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "url_model": {
    "probability": 0.25,
    "label": "BENIGN",
    "confidence": 0.92,
    "explanations": [...],
    "model_name": "URL Model"
  },
  "html_model": {
    "probability": 0.15,
    "label": "BENIGN",
    "confidence": 0.88,
    "explanations": [...],
    "model_name": "HTML Model"
  },
  "dom_model": {
    "probability": 0.20,
    "label": "BENIGN",
    "confidence": 0.85,
    "explanations": [...],
    "model_name": "DOM Model"
  },
  "ensemble": {
    "probability": 0.20,
    "label": "BENIGN",
    "confidence": 0.88,
    "explanations": [...],
    "model_name": "Ensemble"
  }
}
```

### POST `/api/analyze_html_file`
Analyze HTML content

**Request:**
```json
{
  "html": "<html><body>...</body></html>"
}
```

**Response:** Same as `/api/analyze_url_full`

## 🎨 UI Components

The frontend uses shadcn/ui for consistent, accessible components:

- **Button**: Primary CTA, with variants (default, outline, ghost)
- **Card**: Content containers
- **Input**: Text input fields
- **Tabs**: Tab navigation (URL vs HTML)
- **Badge**: Status indicators
- **Progress**: Confidence meter
- **Alert**: Error/info messages
- **Toaster**: Toast notifications
- **Dialog**: Modal dialogs
- **And 40+ other components**

See `src/components/ui/` for all available components.

## 🌙 Dark Mode

The app supports light and dark themes:

- Toggle via the 🌙/☀️ button in the header
- Preference saved to `localStorage`
- Uses Tailwind CSS dark mode class strategy
- All components inherit theme colors

## 📊 Result Display

### Risk Levels

- **LOW** (< 33%): Green - Likely legitimate
- **MEDIUM** (33-67%): Yellow - Uncertain
- **HIGH** (> 67%): Red - Likely phishing

### Explanations

Each model provides explanations for its verdict:
- URL patterns and characteristics
- HTML content analysis
- DOM structure features

### Confidence Score

Indicates how certain the model is about its prediction (0-100%).

## 🧪 Testing

### Lint Code

```bash
npm run lint
```

Runs ESLint to check code quality and style.

### Test URLs

Use these for testing:

**Phishing URLs:**
- `https://malicious.com`
- `https://fake-bank.example.com`

**Legitimate URLs:**
- `https://google.com`
- `https://github.com`

## 📱 Responsive Design

The app is fully responsive:

- **Mobile**: Full width, stacked layout
- **Tablet**: 2-column layout
- **Desktop**: 3-column with history sidebar

Breakpoints:
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px

## ⌨️ Keyboard Shortcuts

- **Enter**: Submit URL analysis (when input focused)
- **Tab**: Navigate between elements
- **Ctrl+C**: Copy results to clipboard

## 🐛 Troubleshooting

### API Connection Issues

**Error: "Failed to fetch from backend"**

1. Ensure backend is running on `http://localhost:8002`
2. Check `VITE_API_URL` environment variable
3. Verify CORS is enabled on backend
4. Check browser console for network errors

### Port Already in Use

**Error: "Port 8080 already in use"**

```bash
# Use a different port
npm run dev -- --port 3000
```

### Slow Performance

1. Check network latency to backend
2. Clear browser cache and local storage
3. Try incognito/private mode
4. Use production build: `npm run build && npm run preview`

### Dark Mode Not Persisting

1. Check if `localStorage` is enabled
2. Clear site data and reload
3. Try incognito mode

## 📚 Dependencies

### Main Dependencies

```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "react-router-dom": "^6.30.1",
  "@tanstack/react-query": "^5.83.0",
  "react-hook-form": "^7.61.1",
  "zod": "^3.25.76",
  "tailwindcss": "^3.4.17",
  "@radix-ui/*": "latest"
}
```

### Dev Dependencies

```json
{
  "vite": "^5.4.19",
  "typescript": "^5.8.3",
  "eslint": "^9.32.0",
  "@vitejs/plugin-react-swc": "^3.11.0"
}
```

See `package.json` for complete list with versions.

## 🚀 Deployment

### Quick Deploy (Build + Run from Dist)

```bash
# One-line command to build and run from dist folder
bun run build:prod
# or with npm
npm run build:prod
```

This builds the optimized production files and immediately runs them from the `dist/` folder. Perfect for testing before full deployment.

### Deploy to Railway

1. **Create Railway Project**
   ```bash
   railway init
   ```

2. **Configure build command**
   ```bash
   npm run build
   ```

3. **Configure start command**
   ```bash
   npm run preview
   ```

4. **Set environment variables**
   ```
   VITE_API_URL=https://your-backend-url.com
   ```

5. **Deploy**
   ```bash
   railway up
   ```

### Deploy to Vercel

1. **Connect GitHub repository**
2. **Vercel auto-detects Vite**
3. **Build command**: `npm run build`
4. **Output directory**: `dist`
5. **Environment variables**: Set `VITE_API_URL`

### Deploy to Netlify

1. **Connect GitHub repository**
2. **Build command**: `npm run build`
3. **Publish directory**: `dist`
4. **Environment variables**: Set `VITE_API_URL`

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json bun.lockb ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
EXPOSE 8080
CMD ["serve", "-s", "dist", "-l", "8080"]
```

Build and run:
```bash
docker build -t url-guardian-frontend .
docker run -p 8080:8080 url-guardian-frontend
```

## 🤝 Contributing

### Code Style

- Use TypeScript for type safety
- Follow ESLint rules
- Use React hooks (no class components)
- Component naming: PascalCase
- File naming: kebab-case for files, PascalCase for React components

### Adding New Features

1. Create a new component in `src/components/`
2. Add new pages to `src/pages/`
3. Update routing in `App.tsx`
4. Update README with changes

### Creating New UI Components

1. Use shadcn/cli:
   ```bash
   npx shadcn-ui@latest add [component-name]
   ```
2. Customize in `src/components/ui/`
3. Import and use in pages

## 📄 File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── NavLink.tsx
│   │   └── ui/                # shadcn/ui components
│   ├── hooks/
│   │   ├── use-mobile.tsx
│   │   └── use-toast.ts
│   ├── lib/
│   │   └── utils.ts
│   ├── pages/
│   │   ├── Index.tsx
│   │   ├── IndexNew.tsx
│   │   └── NotFound.tsx
│   ├── App.tsx
│   ├── App.css
│   ├── main.tsx
│   ├── index.css
│   └── vite-env.d.ts
├── public/
│   └── robots.txt
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── postcss.config.js
├── package.json
├── bun.lockb
├── eslint.config.js
├── components.json
├── index.html
└── README.md
```

## 🔗 Integration with Backend

The frontend connects to the backend for analysis:

1. **Backend must be running** on `http://localhost:8002` (or configured URL)
2. **CORS** must be enabled on the backend
3. **API endpoints** must match frontend expectations

Backend endpoints required:
- `POST /api/analyze_url_full`
- `POST /api/analyze_html_file`

See backend README for setup instructions.

## 📞 Support & Issues

For issues or questions:

1. Check the **Troubleshooting** section above
2. Review browser console for errors
3. Check backend logs for API issues
4. Create an issue in the repository

## 📄 License

[Add your license here]

## ✉️ Contact

For questions or support, contact:
- **Email**: [Your Email]
- **Repository**: [GitHub Link]

---

**Happy phishing detecting! 🎣🔒**
