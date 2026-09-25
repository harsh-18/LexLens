# LexLens Development & Contribution Guide

## 1. Local Environment Setup

1. **Python Environment**:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r backend/requirements.txt
```

2. **Node Environment**:
```bash
cd frontend
npm install
cd ..
```

3. **Environment Variables**:
Create `.env` based on `.env.example`:
```ini
GOOGLE_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./lexlens.db
STORAGE_DIR=./storage
JWT_SECRET=your_jwt_secret
```

---

## 2. Running Locally

### Option A: Unified FastAPI Server (Serves API + Built UI)
```bash
# Build frontend static bundle
cd frontend && npm run build && cd ..

# Run backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
# Access at http://127.0.0.1:8000
```

### Option B: Dual Development Server (Hot Reloading)
- Backend: `python -m uvicorn backend.app.main:app --reload --port 8000`
- Frontend: `cd frontend && npm run dev` (Runs on port 5173 with proxy to 8000)

---

## 3. Running Automated Tests

Run the full pytest suite:
```bash
python -m pytest backend/tests -v
```
Test suite includes:
- `test_parsers.py`: Multi-format parsing & page metadata
- `test_security.py`: Password hashing & prompt injection defenses
- `test_contradiction.py`: Inconsistency detection logic
- `test_retrieval_and_claims.py`: BM25 scoring & claim validation
- `test_api_endpoints.py`: End-to-end FastAPI test client execution
