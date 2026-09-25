# LexLens 🔍⚖️
> **Know what you signed. Know what it means. Know what to ask next.**

LexLens is a production-grade, AI-native legal document intelligence and navigation platform built for non-lawyers. Instead of superficial summarization or simple chatbot wrappers, LexLens parses legal contracts into structured relational knowledge graphs—extracting obligations, rights, deadlines, cross-clause contradictions, and absent protections with direct, verifiable citations back to the source text.

---

## 🌟 Key Differentiators

1. **Structured Legal Knowledge Graph**:
   - Converts legal prose into structured entities: Parties, Clauses, Obligations (Actor, Action, Trigger, Deadline, Condition), Rights, Restrictions, and Financial Terms.
   - Preserves legal ambiguity rather than hallucinating certainty.

2. **Flagship Contradiction Detection**:
   - Automatically uncovers cross-clause conflicts (e.g., Clause 4.1 requiring payment in 30 days vs Schedule B specifying 60 days; or asymmetric termination notice windows).

3. **Audited Missing Protections**:
   - Detects absent standard clauses (e.g., Liability Caps, Pre-Existing IP Carve-outs, Mutual Confidentiality) using legally neutral framing: *"Not found in the analyzed document."*

4. **Evidence-Grounded RAG with Claim Validation**:
   - Hybrid retrieval combining dense vector similarity (`gemini-embedding-001`), sparse BM25 keyword matching, and Reciprocal Rank Fusion (RRF).
   - Post-generation Claim Validation layer checking generated claims against retrieved evidence.

5. **Contract Version Comparison**:
   - Side-by-side diffing of modified clauses, shifted deadlines, revised obligations, and changing risk allocations between contract versions.

6. **Lawyer Consultation Brief**:
   - Generates an attorney briefing packet with relevant facts, critical clauses, and high-impact questions to ask counsel.

7. **Strict Security & Prompt Injection Defense**:
   - Treats uploaded contracts as untrusted data using strict delimiter encapsulation (`<untrusted_document_data>`) and instruction sanitization.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Google Gemini API Key (`GOOGLE_API_KEY`)

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/LexLens.git
cd LexLens

# Configure environment
cp .env.example .env
# Ensure GOOGLE_API_KEY is set in .env

# Install backend dependencies
pip install -r backend/requirements.txt

# Run backend tests
python -m pytest backend/tests -v

# Start FastAPI Server (serves both API and UI)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Development (Optional for Hot Reloading)
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## 🧪 Automated Evaluation Benchmark

LexLens features an automated evaluation suite testing:
- Straightforward clause retrieval
- Cross-clause contradiction detection
- Negative case / absent term rejection
- Prompt injection resistance
- Numerical financial figure recall

Run the tests via API:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/evaluation/run
```
Or run pytest locally:
```bash
python -m pytest backend/tests -v
```

---

## 📂 Architecture

```
LexLens/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app & static file mounting
│   │   ├── config.py            # Pydantic settings & env management
│   │   ├── database.py          # SQLAlchemy session & SQLite engine
│   │   ├── models/              # Normalized legal schema (Clauses, Obligations, etc.)
│   │   ├── schemas/             # Pydantic validation & response models
│   │   ├── api/                 # Modular REST API endpoints
│   │   └── services/            # Chunker, Hybrid RAG, Extractor, Contradictions, Security
│   └── tests/                   # 12 automated unit & integration tests
├── frontend/
│   ├── src/
│   │   ├── components/          # 3-Panel workspace, viewer, modals, intelligence tabs
│   │   ├── services/api.ts      # Type-safe API client
│   │   ├── types/               # TypeScript data definitions
│   │   └── index.css            # Custom glassmorphic Vanilla CSS design system
│   └── dist/                    # Production bundle served by FastAPI
├── ARCHITECTURE.md              # System design & data flow
├── SECURITY.md                  # Security controls & prompt injection defense
├── AI.md                        # Model providers, prompts, and grounding
├── EVALUATION.md                # Benchmark metrics & methodology
├── API.md                       # Complete REST API reference
└── DEVELOPMENT.md               # Developer setup & contribution guidelines
```
