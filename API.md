# LexLens REST API Reference

Base URL: `/api/v1`

---

## 1. Authentication (`/auth`)

### `POST /auth/register`
Register a new user account.
```json
{
  "email": "user@example.com",
  "password": "Password123!",
  "full_name": "Jane Doe"
}
```

### `POST /auth/login`
Authenticate with email and password. Returns JWT bearer token.

### `POST /auth/demo-session`
Initializes a demo session with pre-seeded legal agreements and returns an authenticated demo token.

---

## 2. Documents (`/documents`)

### `POST /documents/upload`
Upload a PDF, DOCX, or TXT document (multipart/form-data).
Returns: `DocumentMetadataResponse`.

### `GET /documents`
List all ingested documents for the authenticated tenant.

### `GET /documents/{id}`
Retrieve complete document detail including pages and extracted legal analysis.

### `DELETE /documents/{id}`
Securely delete document, file storage, and associated legal relational entities.

---

## 3. Analysis & Intelligence (`/documents/{id}`)

### `POST /documents/{id}/analyze`
Triggers the multi-stage document intelligence pipeline:
- Chunking & Gemini embedding generation
- Entity & party extraction
- 23-category taxonomy clause classification
- Obligation, right, deadline, and restriction extraction
- Cross-clause contradiction detection
- Missing protections audit

### `GET /documents/{id}/analysis`
Fetch already computed structured legal analysis.

---

## 4. Grounded Q&A (`/documents/{id}/ask`)

### `POST /documents/{id}/ask`
Perform grounded retrieval-augmented reasoning over the document:
```json
{
  "question": "Can the company terminate me without cause?",
  "clause_filter": "Termination"
}
```
Response:
```json
{
  "question": "Can the company terminate me without cause?",
  "answer": "Yes, under Clause 5.2 (Page 2), the company may terminate your employment without Cause upon thirty (30) days prior written notice...",
  "citations": [
    {
      "document_name": "Senior AI Architect Employment Agreement (v1)",
      "clause_number": "5.2",
      "page_number": 2,
      "excerpt": "Company may terminate Employee's employment without Cause upon thirty (30) days prior written notice..."
    }
  ],
  "unsupported_claims": [],
  "is_grounded": true,
  "groundedness_score": 1.0,
  "latency_ms": 142.5,
  "token_usage": 320
}
```

---

## 5. Contract Comparison (`/comparisons`)

### `POST /comparisons`
Compare two contract versions:
```json
{
  "document_a_id": "demo-doc-employment-v1",
  "document_b_id": "demo-doc-employment-v2"
}
```

---

## 6. Lawyer Consultation Brief (`/documents/{id}/consultation-brief`)

### `POST /documents/{id}/consultation-brief`
Generates a structured client legal briefing memo with tailored questions for counsel.

---

## 7. Benchmarks & Observability

### `POST /evaluation/run`
Executes automated groundness and precision test suites.

### `GET /metrics`
Returns system observability metrics: latencies, document counts, and model configurations.
