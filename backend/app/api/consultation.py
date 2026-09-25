from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.schemas.consultation import ConsultationBriefResponse
from backend.app.services.security import get_current_user, verify_document_ownership
from backend.app.services.consultation_brief import ConsultationBriefService

router = APIRouter(prefix="/documents", tags=["Consultation"])

@router.post("/{document_id}/consultation-brief", response_model=ConsultationBriefResponse)
def generate_consultation_brief(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = verify_document_ownership(document_id, current_user, db)
    
    doc_dict = {
        "id": doc.id,
        "title": doc.title,
        "document_type": doc.document_type,
        "jurisdiction": doc.jurisdiction,
        "summary": doc.summary or "Legal document under review.",
        "clauses": [
            {
                "clause_number": c.clause_number,
                "category": c.category,
                "title": c.title,
                "text": c.text,
                "plain_explanation": c.plain_explanation,
                "risk_note": c.risk_note
            }
            for c in doc.clauses
        ],
        "contradictions": [
            {
                "title": ct.title,
                "clause_a": ct.clause_a,
                "clause_b": ct.clause_b,
                "explanation": ct.explanation
            }
            for ct in doc.contradictions
        ],
        "missing_protections": [
            {
                "protection_type": m.protection_type,
                "description": m.description,
                "recommendation": m.recommendation
            }
            for m in doc.missing_protections
        ]
    }

    brief = ConsultationBriefService.generate_brief(doc_dict)
    return brief
