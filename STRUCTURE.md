# Project Structure

This document describes the reorganized folder structure of the DATN-demo project.

## Overview

The project is organized into logical domains to support clarity, deployment, and team collaboration.

```
DATN-demo/
├── backend/                 # Python backend (FastAPI/Flask) for phishing detection API
│   ├── models_src/         # Model inference code (architectures, preprocessing)
│   ├── main.py             # API entry point
│   ├── config.py           # Backend configuration
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # Backend-specific docs
│
├── frontend/                # React TypeScript frontend (Vite)
│   ├── src/                # React source code
│   │   ├── components/     # Reusable React components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Frontend utilities and helpers
│   │   ├── App.tsx         # Main app component
│   │   └── main.tsx        # Entry point
│   ├── public/             # Static assets (served as-is)
│   ├── package.json        # Frontend dependencies (Node/Bun)
│   ├── vite.config.ts      # Vite build configuration
│   ├── tsconfig.json       # TypeScript config
│   ├── tailwind.config.ts  # Tailwind CSS config
│   ├── postcss.config.js   # PostCSS config
│   ├── eslint.config.js    # ESLint config
│   ├── index.html          # HTML entry point
│   └── components.json     # Shadcn components config
│
├── docs/                    # Comprehensive documentation hub
│   ├── deployment/         # Deployment guides (Railway, etc.)
│   ├── quick-start/        # Quick-start guides for devs and staging
│   ├── technical/          # Technical deep-dives (architecture, decisions)
│   ├── tests/              # Test guides and acceptance criteria
│   ├── reports/            # Status reports, build logs, verification results
│   ├── analysis/           # Analysis docs (phishing patterns, model eval)
│   ├── notes/              # Team notes and handoff docs
│   ├── readmes/            # README variations
│   └── other/              # Miscellaneous docs
│
├── models/                  # Trained model checkpoints and artifacts
│   ├── *.pt                # PyTorch model weights (GNN, RNN, Transformer)
│   ├── *_threshold.json    # Decision thresholds per model
│   ├── *_vocab.json        # Vocabulary files for embeddings
│   ├── *.csv               # Predictions and CV results
│   ├── *.jsonl             # Graph/dataset files
│   └── README.md           # Model inventory and usage guide
│
├── notebooks/              # Jupyter notebooks (research, experiments)
│   └── *.ipynb             # Notebook files
│
├── scripts/                # Automation and utility scripts
│   ├── launch_app.py       # App launcher
│   ├── run_backend.py      # Backend runner
│   ├── start_backend.py    # Backend startup
│   ├── proxy.py            # Proxy utility
│   └── setup.sh            # Environment setup
│
├── configs/                # Configuration files (centralized)
│   ├── tsconfig.json       # TypeScript config
│   ├── tailwind.config.ts  # Tailwind CSS config
│   ├── postcss.config.js   # PostCSS config
│   ├── eslint.config.js    # ESLint config
│   └── vite.config.ts      # Vite build config (at root, can symlink)
│
├── tests/                  # Integration and backend tests
│   ├── test_endpoint.py    # API endpoint tests
│   ├── test_full_pipeline.py
│   ├── verify_normalize.py
│   └── (pytest configs)
│
├── package.json            # Placeholder (real package.json is in frontend/)
├── README.md               # Root project README

```

## Directory Responsibilities

| Folder | Purpose | Owner | Key Files |
|--------|---------|-------|-----------|
| `backend/` | Python API, model serving, inference | Backend team | `main.py`, `requirements.txt` |
| `frontend/` | React UI, components, Vite build | Frontend team | `src/App.tsx`, `package.json`, `vite.config.ts` |
| `docs/` | All project documentation | Entire team | `deployment/`, `quick-start/`, `technical/` |
| `models/` | Trained model weights, artifacts | ML / Backend | `*.pt`, `*_threshold.json` |
| `notebooks/` | Experimental Jupyter notebooks | ML / Research | `*.ipynb` |
| `scripts/` | Helper scripts, automation | DevOps / Backend | `setup.sh`, `run_backend.py` |
| `configs/` | Shared tool configs (if any) | DevOps | `(empty or shared configs)` |
| `tests/` | Integration & unit tests | QA / Backend | `test_*.py` |

## Migration Notes

This structure was reorganized on **Nov 28, 2025**:
- **Phase 1:** `docs-collected/` → `docs/`, `CKPT/` → `models/`, scripts → `scripts/`
- **Phase 2:** Frontend/backend split:
  - `src/` → `frontend/src/`
  - `public/` → `frontend/public/`
  - `package.json`, `vite.config.ts`, `index.html` → `frontend/`
  - Frontend configs (`tsconfig.*`, `eslint.config.js`, `tailwind.config.ts`) → `frontend/`

## Quick References

### Start Development

```bash
# Frontend (from frontend/)
cd frontend
npm install
npm run dev

# Backend (from backend/)
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

### Deploy to Staging

See `docs/deployment/DEPLOYMENT_GUIDE.md` for step-by-step instructions.

### Run Tests

```bash
# Backend tests
cd tests
pytest test_endpoint.py
python test_full_pipeline.py
```

### View Documentation

- **Getting started:** `docs/quick-start/QUICK_START.md`
- **Architecture:** `docs/technical/IMPLEMENTATION_COMPLETE.md`
- **Deployment:** `docs/deployment/DEPLOYMENT_GUIDE.md`
- **Model info:** `models/README.md`

## CI/CD Integration

When setting up CI/CD (GitHub Actions, etc.):
- Place workflows in `.github/workflows/`
- Reference scripts in `scripts/` for build/test/deploy steps
- Model artifacts stay in `models/` (consider git-lfs or external storage)
- Tests use files in `tests/`

## Future Improvements

- [ ] Add `.gitkeep` files to empty folders to preserve structure
- [ ] Create `docker/` for frontend and backend Dockerfiles
- [ ] Add `infra/` for infrastructure-as-code (Terraform, K8s manifests)
- [ ] Set up `CODEOWNERS` file to clarify review responsibilities (frontend/ vs backend/)
- [ ] Add GitHub Actions workflows in `.github/workflows/` for frontend build/deploy and backend tests
