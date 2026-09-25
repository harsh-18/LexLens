from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TestCaseResult(BaseModel):
    test_id: str
    category: str
    name: str
    passed: bool
    groundedness: float
    citation_precision: float
    unsupported_claims_detected: int
    latency_ms: float
    notes: Optional[str] = None

class EvaluationReportResponse(BaseModel):
    evaluation_id: str
    timestamp: str
    overall_score: float
    groundedness_score: float
    citation_coverage: float
    unsupported_claim_rate: float
    avg_latency_ms: float
    total_tests: int
    passed_tests: int
    results: List[TestCaseResult] = []
