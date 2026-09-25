# LexLens Architecture & System Design
**Platform**: AI-Native Legal Document Intelligence & Navigation Assistant  
**Tagline**: *Know what you signed. Know what it means. Know what to ask next.*

---

## 1. System Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LexLens Web Application                         │
│   Landing Page │ Interactive Workspace │ Hybrid Chat │ Version Diff    │
│   Timeline View │ Clause Explorer │ Lawyer Consultation Brief Generator │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ JSON REST / SSE
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Application Gateway                     │
│   Auth & User Isolation │ Rate Limiter │ Prompt Injection Sanitizer    │
│   Document Ingestion & Multi-Format Parser (PDF, DOCX, TXT)           │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
      ┌──────────────────────────────┴──────────────────────────────┐
      ▼                                                             ▼
┌──────────────────────────────┐              ┌──────────────────────────────┐
│  Document Intelligence Engine │              │      Hybrid RAG & Reasoning  │
│  - Layout & Page Segmentation│              │  - Dense Vectors (Gemini)    │
│  - Clause Classifier (23 cat)│              │  - BM25 Sparse Search        │
│  - Entity & Party Extractor  │              │  - Reciprocal Rank Fusion    │
│  - Obligation Graph Builder  │              │  - Cross-Reference Traversal │
│  - Rights & Restrictions     │              │  - Grounded Claim Validator  │
│  - Deadlines & Timeline      │              │  - Source Citation Resolver  │
│  - Contradiction Detector    │              └──────────────┬───────────────┘
│  - Missing Protection Audit  │                             │
└──────────────┬───────────────┘                             │
               │                                             │
               ▼                                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Storage & Intelligence Layer                    │
│   SQLite / SQLAlchemy (Normalized Legal Schema: Clauses, Obligations,  │
│   Rights, Deadlines, Inconsistencies, Vector Chunks)                  │
│   File Vault (Isolated per-tenant documents)                           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Modules

### 2.1 Backend (`backend/app/`)
1. **API Layer (`api/`)**:
   - `auth.py`: JWT token generation, password hashing, demo session bootstrap.
   - `documents.py`: Document upload, metadata extraction, validation, deletion.
   - `analysis.py`: Trigger pipeline, fetch structured clauses, obligations, contradictions, missing protections.
   - `qa.py`: Hybrid retrieval, LLM reasoning, claim verification, citation generation.
   - `compare.py`: Contract comparison engine (v1 vs v2 clause and obligation diffs).
   - `consultation.py`: Lawyer consultation brief compilation.
   - `metrics.py`: Observability telemetry (latency, token usage, groundedness scores).
   - `evaluation.py`: Automated evaluation runner and benchmarks.

2. **Core Services (`services/`)**:
   - `parser.py`: Robust text/layout extraction for PDF, DOCX, TXT with page and section preservation.
   - `ai_providers.py`: Extensible provider interface (`LLMProvider`, `EmbeddingProvider`) supporting Gemini (`gemini-3.8-flash` & `gemini-embedding-001`), OpenAI, and deterministic offline fallbacks.
   - `extractor.py`: Structured extraction using schema-constrained JSON (parties, obligations, rights, deadlines, restrictions).
   - `contradiction.py`: Multi-clause consistency checker detecting conflicting payment terms, notice requirements, etc.
   - `missing_protections.py`: Missing protection auditor (liability cap, mutual confidentiality, non-solicitation).
   - `retrieval.py`: Hybrid search combining BM25 keyword matching, Gemini dense vector cosine similarity, and Reciprocal Rank Fusion (RRF).
   - `claim_validator.py`: Post-generation claim verifier ensuring claims are directly traceable to retrieved chunks.
   - `security.py`: Prompt-injection defense boundaries (`<untrusted_document_data>`), path traversal prevention, role-based document authorization.
   - `demo_seeder.py`: Ready-to-use realistic legal contracts with deterministic pre-analyzed fixtures for 1-click evaluation.

3. **Data Models (`models/`)**:
   - Normalized relational tables in SQLite for Documents, Pages, Chunks, Clauses, Parties, Obligations, Rights, Deadlines, Restrictions, Contradictions, Missing Protections, and Q&A history.

### 2.2 Frontend (`frontend/`)
- Pure modern Vanilla CSS system (custom design tokens, glassmorphic cards, responsive panels, typography, accessible contrast, smooth micro-interactions).
- React 19 + TypeScript + Vite.
- 3-Panel Document Workspace:
  - Navigation Panel: Clause hierarchy, category filters.
  - Document Viewer: Full text/page view with interactive citation clicking and source highlighting.
  - Intelligence Panel: Tabs for Overview, Obligations Graph, Deadlines Timeline, Contradictions, Missing Protections, and Grounded Q&A Chat.
- Dedicated Comparison View and Lawyer Consultation Brief export.
