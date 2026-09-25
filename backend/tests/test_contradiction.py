import pytest
from backend.app.services.contradiction import ContradictionDetector

def test_rule_based_payment_contradiction():
    clauses = [
        {
            "clause_number": "Clause 4.1",
            "page_start": 2,
            "text": "All invoices shall be settled within thirty (30) days of receipt by Client."
        },
        {
            "clause_number": "Schedule B",
            "page_start": 5,
            "text": "Notwithstanding Section 4.1, specialized vendor disbursements are due within sixty (60) days after invoice."
        }
    ]

    contradictions = ContradictionDetector.detect_contradictions(clauses, "")
    assert len(contradictions) >= 1
    c = contradictions[0]
    assert "Payment" in c["title"] or "Notice" in c["title"]
    assert "30" in c["explanation"] and "60" in c["explanation"]

def test_rule_based_notice_period_discrepancy():
    clauses = [
        {
            "clause_number": "Section 5.2",
            "page_start": 2,
            "text": "Employer may terminate this Agreement without Cause upon thirty (30) days prior written notice."
        },
        {
            "clause_number": "Section 18.2",
            "page_start": 6,
            "text": "Employee shall provide ninety (90) days prior written notice prior to voluntary resignation."
        }
    ]

    contradictions = ContradictionDetector.detect_contradictions(clauses, "")
    assert len(contradictions) >= 1
    notice_conflict = [c for c in contradictions if "Notice" in c["title"]]
    assert len(notice_conflict) > 0
    assert "30" in notice_conflict[0]["explanation"] and "90" in notice_conflict[0]["explanation"]
