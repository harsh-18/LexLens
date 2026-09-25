import uuid
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.legal import (
    Page, Chunk, Clause, Party, Obligation, Right, Deadline,
    Restriction, FinancialTerm, Contradiction, MissingProtection
)
from backend.app.schemas.legal import (
    FullAnalysisResponse, PartySchema, ClauseSchema, ObligationSchema,
    RightSchema, DeadlineSchema, RestrictionSchema, FinancialTermSchema,
    ContradictionSchema, MissingProtectionSchema
)
from backend.app.services.security import get_current_user, verify_document_ownership
from backend.app.services.chunker import LegalChunker
from backend.app.services.extractor import LegalExtractor
from backend.app.services.contradiction import ContradictionDetector
from backend.app.services.missing_protections import MissingProtectionAuditor
from backend.app.services.ai_providers import AIProviderFactory
from backend.app.services.cache import document_cache, query_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Analysis"])

def execute_analysis_pipeline(document_id: str, db: Session):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return

    try:
        doc.status = "processing"
        db.commit()

        pages = db.query(Page).filter(Page.document_id == document_id).order_by(Page.page_number).all()
        full_text = "\n\n".join([f"--- Page {p.page_number} ---\n{p.text}" for p in pages])
        pages_summary = [{"page_number": p.page_number, "length": len(p.text)} for p in pages]

        # 1. Structured Chunking & Vector Generation
        chunks = LegalChunker.chunk_document(
            document_id=doc.id,
            pages=pages,
            document_type=doc.document_type
        )
        embed_provider = AIProviderFactory.get_embedding_provider()
        
        # Clear existing chunks and query cache
        db.query(Chunk).filter(Chunk.document_id == document_id).delete()
        query_cache.clear()
        
        # Batch embedding computation for maximum throughput
        chunk_texts = [chk.text for chk in chunks]
        try:
            embeddings = embed_provider.embed_texts(chunk_texts)
        except Exception as e:
            logger.warning(f"Batch embedding fallback: {e}")
            embeddings = [None] * len(chunks)

        chunk_records = []
        for chk, emb in zip(chunks, embeddings):
            emb_json = json.dumps(emb) if emb else None
            chunk_records.append(Chunk(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                page_number=chk.page_number,
                section=chk.section,
                clause_id=chk.clause_id,
                text=chk.text,
                embedding_json=emb_json
            ))
        db.add_all(chunk_records)
        db.commit()

        # 2. Extract Document Intelligence
        extracted = LegalExtractor.extract_document_intelligence(
            full_text=full_text,
            pages_summary=pages_summary,
            document_filename=doc.filename
        )

        doc.document_type = extracted.get("document_type", doc.document_type)
        doc.jurisdiction = extracted.get("jurisdiction", doc.jurisdiction)
        doc.language = extracted.get("language", doc.language)
        doc.summary = extracted.get("summary", "Document analyzed by LexLens.")

        # Clear previous extracted relations if re-analyzing
        db.query(Party).filter(Party.document_id == document_id).delete()
        db.query(Clause).filter(Clause.document_id == document_id).delete()
        db.query(Obligation).filter(Obligation.document_id == document_id).delete()
        db.query(Right).filter(Right.document_id == document_id).delete()
        db.query(Deadline).filter(Deadline.document_id == document_id).delete()
        db.query(Restriction).filter(Restriction.document_id == document_id).delete()
        db.query(FinancialTerm).filter(FinancialTerm.document_id == document_id).delete()
        db.query(Contradiction).filter(Contradiction.document_id == document_id).delete()
        db.query(MissingProtection).filter(MissingProtection.document_id == document_id).delete()

        # Bulk Save Parties
        parties_to_add = [
            Party(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                name=p.get("name", "Unknown Party"),
                role=p.get("role", "Party"),
                party_type=p.get("party_type", "Entity")
            )
            for p in extracted.get("parties", [])
        ]
        db.add_all(parties_to_add)

        # Bulk Save Clauses
        extracted_clauses = extracted.get("clauses", [])
        clauses_to_add = [
            Clause(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                clause_number=c.get("clause_number"),
                title=c.get("title"),
                text=c.get("text", ""),
                page_start=c.get("page_start", 1),
                page_end=c.get("page_end", 1),
                category=c.get("category", "Miscellaneous"),
                plain_explanation=c.get("plain_explanation"),
                risk_note=c.get("risk_note"),
                questions_to_ask=json.dumps(c.get("questions_to_ask", []))
            )
            for c in extracted_clauses
        ]
        db.add_all(clauses_to_add)

        # Bulk Save Obligations
        obligations_to_add = [
            Obligation(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                actor=o.get("actor", "Party"),
                action=o.get("action", ""),
                target_object=o.get("target_object"),
                trigger=o.get("trigger"),
                deadline=o.get("deadline"),
                duration=o.get("duration"),
                condition=o.get("condition"),
                is_ambiguous=o.get("is_ambiguous", False),
                ambiguity_reason=o.get("ambiguity_reason"),
                source_clause_number=o.get("source_clause_number"),
                source_page=o.get("source_page", 1),
                excerpt=o.get("excerpt")
            )
            for o in extracted.get("obligations", [])
        ]
        db.add_all(obligations_to_add)

        # Bulk Save Rights
        rights_to_add = [
            Right(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                holder=r.get("holder", "Party"),
                right_text=r.get("right_text", ""),
                condition=r.get("condition"),
                source_clause_number=r.get("source_clause_number"),
                source_page=r.get("source_page", 1),
                excerpt=r.get("excerpt")
            )
            for r in extracted.get("rights", [])
        ]
        db.add_all(rights_to_add)

        # Bulk Save Deadlines
        deadlines_to_add = [
            Deadline(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                event=d.get("event", "Milestone"),
                duration_or_date=d.get("duration_or_date", "Date"),
                triggering_condition=d.get("triggering_condition"),
                category=d.get("category", "Notice"),
                order_index=idx,
                source_clause_number=d.get("source_clause_number"),
                source_page=d.get("source_page", 1)
            )
            for idx, d in enumerate(extracted.get("deadlines", []), start=1)
        ]
        db.add_all(deadlines_to_add)

        # Bulk Save Restrictions
        restrictions_to_add = [
            Restriction(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                restriction_type=rst.get("restriction_type", "Restriction"),
                restricted_party=rst.get("restricted_party", "Party"),
                activity=rst.get("activity", ""),
                duration=rst.get("duration"),
                scope=rst.get("scope"),
                source_clause_number=rst.get("source_clause_number"),
                source_page=rst.get("source_page", 1)
            )
            for rst in extracted.get("restrictions", [])
        ]
        db.add_all(restrictions_to_add)

        # Bulk Save Financial Terms
        financial_terms_to_add = [
            FinancialTerm(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                item=f.get("item", "Payment"),
                amount=f.get("amount", "$0"),
                currency=f.get("currency", "USD"),
                frequency=f.get("frequency"),
                condition=f.get("condition"),
                source_clause_number=f.get("source_clause_number")
            )
            for f in extracted.get("financial_terms", [])
        ]
        db.add_all(financial_terms_to_add)

        # 3. Detect Contradictions
        contradictions = ContradictionDetector.detect_contradictions(extracted_clauses, full_text)
        contradictions_to_add = [
            Contradiction(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                title=ct.get("title", "Contradiction Detected"),
                clause_a=ct.get("clause_a", "Clause A"),
                text_a=ct.get("text_a", ""),
                page_a=ct.get("page_a", 1),
                clause_b=ct.get("clause_b", "Clause B"),
                text_b=ct.get("text_b", ""),
                page_b=ct.get("page_b", 1),
                explanation=ct.get("explanation", ""),
                severity=ct.get("severity", "Moderate")
            )
            for ct in contradictions
        ]
        db.add_all(contradictions_to_add)

        # 4. Audit Missing Protections
        missing_protections = MissingProtectionAuditor.audit_document(extracted_clauses, full_text, doc.document_type)
        protections_to_add = [
            MissingProtection(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                protection_type=m.get("protection_type", "Protection"),
                description=m.get("description", ""),
                recommendation=m.get("recommendation", ""),
                severity=m.get("severity", "Notice")
            )
            for m in missing_protections
        ]
        db.add_all(protections_to_add)

        doc.status = "analyzed"
        doc.error_message = None
        db.commit()

        # Invalidate document cache to ensure fresh state is delivered
        document_cache.delete(f"{doc.user_id}:{doc.id}")
    except Exception as e:
        logger.error(f"Analysis failed for {document_id}: {e}", exc_info=True)
        doc.status = "failed"
        doc.error_message = str(e)
        db.commit()

@router.post("/{document_id}/analyze", response_model=FullAnalysisResponse)
def trigger_analysis(
    document_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = verify_document_ownership(document_id, current_user, db)
    
    # Run analysis synchronously for immediate responsiveness or fallback
    execute_analysis_pipeline(document_id, db)
    db.refresh(doc)

    if doc.status == "failed":
        raise HTTPException(status_code=500, detail=f"Analysis pipeline failed: {doc.error_message}")

    return FullAnalysisResponse(
        document_id=doc.id,
        title=doc.title,
        document_type=doc.document_type,
        jurisdiction=doc.jurisdiction,
        language=doc.language,
        summary=doc.summary,
        page_count=doc.page_count,
        parties=[PartySchema.model_validate(p) for p in doc.parties],
        clauses=[ClauseSchema.model_validate(c) for c in doc.clauses],
        obligations=[ObligationSchema.model_validate(o) for o in doc.obligations],
        rights=[RightSchema.model_validate(r) for r in doc.rights],
        deadlines=[DeadlineSchema.model_validate(d) for d in doc.deadlines],
        restrictions=[RestrictionSchema.model_validate(rst) for rst in doc.restrictions],
        financial_terms=[FinancialTermSchema.model_validate(f) for f in doc.financial_terms],
        contradictions=[ContradictionSchema.model_validate(ct) for ct in doc.contradictions],
        missing_protections=[MissingProtectionSchema.model_validate(m) for m in doc.missing_protections]
    )

@router.get("/{document_id}/analysis", response_model=FullAnalysisResponse)
def get_analysis(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = verify_document_ownership(document_id, current_user, db)
    if doc.status != "analyzed":
        raise HTTPException(status_code=400, detail=f"Document analysis status is '{doc.status}'. Trigger analysis first.")

    return FullAnalysisResponse(
        document_id=doc.id,
        title=doc.title,
        document_type=doc.document_type,
        jurisdiction=doc.jurisdiction,
        language=doc.language,
        summary=doc.summary,
        page_count=doc.page_count,
        parties=[PartySchema.model_validate(p) for p in doc.parties],
        clauses=[ClauseSchema.model_validate(c) for c in doc.clauses],
        obligations=[ObligationSchema.model_validate(o) for o in doc.obligations],
        rights=[RightSchema.model_validate(r) for r in doc.rights],
        deadlines=[DeadlineSchema.model_validate(d) for d in doc.deadlines],
        restrictions=[RestrictionSchema.model_validate(rst) for rst in doc.restrictions],
        financial_terms=[FinancialTermSchema.model_validate(f) for f in doc.financial_terms],
        contradictions=[ContradictionSchema.model_validate(ct) for ct in doc.contradictions],
        missing_protections=[MissingProtectionSchema.model_validate(m) for m in doc.missing_protections]
    )
