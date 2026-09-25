# LexLens AI System & RAG Architecture

## 1. Provider Abstraction

LexLens implements an extensible provider interface (`BaseLLMProvider` and `BaseEmbeddingProvider`) in `backend/app/services/ai_providers.py`:
- **Default LLM**: Google Gemini 3.8 Flash (`gemini-3.8-flash`) via official `google.genai` SDK.
- **Default Embeddings**: Google Gemini Embeddings (`gemini-embedding-001`, 3072 dimensions).
- **Fallback Offline Provider**: Hash-based deterministic pseudo-embedding (384 dimensions) for local unit testing and zero-network test suite execution.

---

## 2. Hybrid Retrieval Architecture (Hybrid RAG)

LexLens implements a multi-stage retrieval pipeline:

```
User Query
    │
    ▼
Sanitization & Guardrails (Prompt Injection Shield)
    │
    ├─────────────────────────────┬─────────────────────────────┐
    ▼                             ▼                             ▼
Dense Vector Retrieval     Sparse BM25 Keyword Search    Metadata / Clause Filter
(Gemini 3072-dim Cosine)    (k1=1.5, b=0.75 Saturation)   (Clause & Section Scope)
    │                             │                             │
    └─────────────────────────────┼─────────────────────────────┘
                                  ▼
                     Reciprocal Rank Fusion (RRF)
                  Score = Σ 1 / (60 + Rank_i)
                                  │
                                  ▼
                     Top-K Evidence Candidates
                                  │
                                  ▼
                   Delimiter-Shielded Context Build
               <untrusted_document_data> ... </untrusted_document_data>
                                  │
                                  ▼
                     Gemini 3.8 Flash Reasoning
                                  │
                                  ▼
                      Claim Validation Layer
              (Verifies Numerical, Date & Statutory Claims)
                                  │
                                  ▼
                      Grounded Response + Citations
```

---

## 3. Schema-Constrained Extraction

All legal extraction runs against rigid Pydantic validation:
- **Parties**: `name`, `role`, `party_type`
- **Clauses**: `clause_number`, `title`, `category` (23 legal taxonomy classes), `plain_explanation`, `risk_note`
- **Obligations**: `actor`, `action`, `target_object`, `trigger`, `deadline`, `duration`, `is_ambiguous`, `ambiguity_reason`
- **Rights**: `holder`, `right_text`, `condition`
- **Deadlines**: `event`, `duration_or_date`, `triggering_condition`, `category`
- **Contradictions**: `title`, `clause_a`, `text_a`, `clause_b`, `text_b`, `explanation`, `severity`
- **Missing Protections**: `protection_type`, `description`, `recommendation`, `severity`
