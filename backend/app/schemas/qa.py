from pydantic import BaseModel
from typing import Optional, List

class Citation(BaseModel):
    document_name: str
    clause_number: str
    page_number: int
    excerpt: str

class QARequest(BaseModel):
    question: str
    clause_filter: Optional[str] = None

class QAResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation] = []
    unsupported_claims: List[str] = []
    is_grounded: bool = True
    groundedness_score: float = 1.0
    latency_ms: float = 0.0
    token_usage: int = 0
