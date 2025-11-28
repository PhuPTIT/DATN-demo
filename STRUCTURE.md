# Project Structure

This document describes the reorganized folder structure of the DATN-demo project for **staging readiness and team collaboration**.

## Quick Overview

The project is split into **frontend**, **backend**, **documentation**, and **assets** for clear separation of concerns and independent CI/CD pipelines.

```
DATN-demo/
├── 📦 backend/              Python FastAPI backend (phishing detection API)
├── 🎨 frontend/             React + Vite frontend (web UI)
├── 📚 docs/                 Comprehensive documentation and guides
├── 🤖 models/               Pre-trained ML model checkpoints
├── 📓 notebooks/            Jupyter notebooks for research
├── 🔧 scripts/              Utility and automation scripts
├── ✅ tests/                Integration and unit tests
└── 📋 STRUCTURE.md          This file
```

## Directory Tree (Full)

```
DATN-demo/
├── backend/                 # 🔵 Python Backend (FastAPI)
│   ├── models_src/         # Model architectures, preprocessing, inference
│   │   ├── architectures.py    # PyTorch models (RNN, Transformer, GCN)
│   │   ├── preprocessing.py    # Input encoding (URL, HTML, DOM)
│   │   └── inference.py        # Model wrappers & ensemble
│   ├── main.py             # FastAPI application & 3 endpoints
│   ├── config.py           # Configuration & model paths
│   ├── requirements.txt    # Python dependencies
│   ├── setup.sh            # Environment setup
│   ├── README.md           # Backend documentation
│   ├── IMPLEMENTATION.md   # Implementation details
│   └── ARCHITECTURE.md     # System architecture
│
├── frontend/                # 🎨 React Frontend (Vite + TypeScript)
│   ├── src/                # Source code
│   │   ├── components/     # React components (UI, helpers)
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── lib/            # Utilities
│   │   ├── App.tsx         # Main app
│   │   └── main.tsx        # Entry point
│   ├── public/             # Static assets
│   ├── package.json        # Dependencies (Node/Bun)
│   ├── vite.config.ts      # Vite build config
│   ├── tsconfig.json       # TypeScript config
│   ├── tailwind.config.ts  # Tailwind CSS
│   ├── eslint.config.js    # Linting rules
│   └── index.html          # HTML entry
│
├── docs/                    # 📚 Documentation Hub
│   ├── deployment/         # Deployment guides (Railway, etc.)
│   ├── quick-start/        # Quick-start for devs & staging
│   ├── technical/          # Architecture, decisions, checklists
│   ├── tests/              # QA test guides
│   ├── reports/            # Build status, verification results
│   ├── analysis/           # Model analysis, phishing patterns
│   ├── notes/              # Team handoff notes
│   ├── readmes/            # README variations
│   └── other/              # Miscellaneous
│
├── models/                  # 🤖 Model Checkpoints & Artifacts
│   ├── *.pt                # PyTorch weights (RNN, Transformer, GCN)
│   ├── *_threshold.json    # Decision thresholds
│   ├── *_vocab.json        # Vocabulary files
│   ├── *.csv               # Predictions, CV results
│   ├── *.jsonl             # Graph, dataset files
│   └── README.md           # Model inventory
│
├── notebooks/              # 📓 Jupyter Notebooks
│   └── *.ipynb             # Research & experiment notebooks
│
├── scripts/                # 🔧 Automation Scripts
│   ├── launch_app.py       # App launcher
│   ├── run_backend.py      # Backend runner
│   ├── start_backend.py    # Backend startup
│   ├── proxy.py            # Proxy utility
│   └── setup.sh            # Environment setup
│
├── tests/                  # ✅ Tests
│   ├── test_endpoint.py    # API endpoint tests
│   ├── test_full_pipeline.py # Pipeline tests
│   └── verify_normalize.py # Data verification
│
└── STRUCTURE.md            # This file
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

This structure was reorganized on **Nov 28, 2025** for staging readiness:

**Phase 1 - Documentation & Assets:**
- `docs-collected/` → `docs/` (with 8 organized subfolders)
- `CKPT/` → `models/` (model checkpoints and artifacts)
- `datn-phishing-fine-tuning-update.ipynb` → `notebooks/`
- Top-level scripts → `scripts/` (launch_app.py, run_backend.py, etc.)
- Test files → `tests/`

**Phase 2 - Frontend/Backend Separation:**
- `src/`, `public/` → `frontend/src/`, `frontend/public/`
- `package.json`, `vite.config.ts`, `bun.lockb` → `frontend/`
- Frontend configs (tsconfig.*, eslint.config.js, tailwind.config.ts) → `frontend/`
- `QUICK_START/` → `quick-start/` (kebab-case naming)
- `HUNG_A_NOTES/` → `notes/` (standardized naming)

**Result:** Clear separation enabling independent deployment and development workflows.

## Quick References

## Start Development

```bash
# Frontend (from frontend/ folder)
cd frontend
npm install
npm run dev

# Backend (from backend/ folder)
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

### Deploy to Staging

See `docs/deployment/DEPLOYMENT_GUIDE.md` for step-by-step platform-specific instructions (e.g., Railway, AWS, GCP).

**Quick outline:**
1. Build frontend: `cd frontend && npm run build`
2. Start backend: `cd backend && python main.py`
3. Point frontend to backend URL
4. Deploy both services to hosting platform

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
