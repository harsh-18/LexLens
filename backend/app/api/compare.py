from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.schemas.comparison import ComparisonResponse
from backend.app.services.security import get_current_user, verify_document_ownership
from backend.app.services.comparison import ContractComparator

router = APIRouter(prefix="/comparisons", tags=["Comparisons"])

class CompareRequest(BaseModel):
    document_a_id: str
    document_b_id: str

@router.post("", response_model=ComparisonResponse)
def compare_contract_versions(
    req: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc_a = verify_document_ownership(req.document_a_id, current_user, db)
    doc_b = verify_document_ownership(req.document_b_id, current_user, db)

    # Convert documents to structured dictionaries
    dict_a = {
        "id": doc_a.id,
        "title": doc_a.title,
        "summary": doc_a.summary or "",
        "clauses": [{"clause_number": c.clause_number, "title": c.title, "text": c.text, "category": c.category} for c in doc_a.clauses],
        "obligations": [{"actor": o.actor, "action": o.action, "deadline": o.deadline} for o in doc_a.obligations]
    }
    dict_b = {
        "id": doc_b.id,
        "title": doc_b.title,
        "summary": doc_b.summary or "",
        "clauses": [{"clause_number": c.clause_number, "title": c.title, "text": c.text, "category": c.category} for c in doc_b.clauses],
        "obligations": [{"actor": o.actor, "action": o.action, "deadline": o.deadline} for o in doc_b.obligations]
    }

    result = ContractComparator.compare_documents(dict_a, dict_b)
    return result
