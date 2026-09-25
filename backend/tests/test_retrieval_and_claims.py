import pytest
from backend.app.services.claim_validator import ClaimValidator
from backend.app.services.retrieval import HybridRetriever

def test_claim_validator_flags_unsupported_numbers():
    chunks = [
        {
            "clause_id": "18.2",
            "section": "Notice Period",
            "page_number": 5,
            "text": "Employee shall provide ninety (90) days written notice prior to departure."
        }
    ]

    # Grounded answer
    grounded_answer = "Under Clause 18.2, you are required to provide 90 days written notice."
    citations, unsupported, score = ClaimValidator.validate_answer(grounded_answer, chunks, "Employment Agreement")
    assert len(citations) == 1
    assert len(unsupported) == 0
    assert score == 1.0

    # Hallucinated answer (asserting 180 days and $50,000 penalty)
    hallucinated_answer = "The employee must give 180 days notice and pay a penalty of $50,000."
    citations, unsupported, score = ClaimValidator.validate_answer(hallucinated_answer, chunks, "Employment Agreement")
    assert len(unsupported) >= 1
    assert score < 1.0

def test_bm25_scoring():
    query_tokens = ["payment", "invoice", "thirty"]
    chunk_matching = "Client shall submit payment for every invoice within thirty calendar days."
    chunk_unrelated = "All dispute matters are subject to governing Delaware jurisdiction."

    score_match = HybridRetriever.bm25_score(query_tokens, chunk_matching)
    score_unrelated = HybridRetriever.bm25_score(query_tokens, chunk_unrelated)

    assert score_match > score_unrelated
    assert score_unrelated == 0.0
