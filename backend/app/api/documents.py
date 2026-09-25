import os
import uuid
import hashlib
from typing import List
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.legal import Page
from backend.app.schemas.document import DocumentMetadataResponse, DocumentDetailResponse
from backend.app.schemas.legal import (
    FullAnalysisResponse, PartySchema, ClauseSchema, ObligationSchema,
    RightSchema, DeadlineSchema, RestrictionSchema, FinancialTermSchema,
    ContradictionSchema, MissingProtectionSchema
)
from backend.app.services.security import get_current_user, verify_document_ownership
from backend.app.services.parser import DocumentParser
from backend.app.services.cache import document_cache, query_cache

router = APIRouter(prefix="/documents", tags=["Documents"])

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

@router.post("/upload", response_model=DocumentMetadataResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    original_filename = file.filename or "uploaded_contract.txt"
    ext = Path(original_filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. LexLens supports PDF, DOCX, and TXT files."
        )

    # Read content
    contents = await file.read()
    file_size = len(contents)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the 25 MB limit.")

    doc_id = str(uuid.uuid4())
    content_hash = hashlib.sha256(contents).hexdigest()

    # Save to storage directory
    user_storage = Path(settings.STORAGE_DIR) / current_user.id
    user_storage.mkdir(parents=True, exist_ok=True)
    saved_file_path = user_storage / f"{doc_id}_{original_filename}"

    with open(saved_file_path, "wb") as f:
        f.write(contents)

    # Multi-format parsing
    parsed_doc = DocumentParser.parse_file(str(saved_file_path), original_filename)

    # Document type detection preliminary
    clean_type = "general_contract"
    lower_name = original_filename.lower()
    if "employment" in lower_name or "job" in lower_name or "offer" in lower_name:
        clean_type = "employment_agreement"
    elif "lease" in lower_name or "rental" in lower_name:
        clean_type = "lease_agreement"
    elif "vendor" in lower_name or "service" in lower_name or "msa" in lower_name:
        clean_type = "vendor_contract"
    elif "nda" in lower_name or "confidential" in lower_name:
        clean_type = "nda"

    # Create Document record
    new_doc = Document(
        id=doc_id,
        user_id=current_user.id,
        title=Path(original_filename).stem.replace("_", " ").title(),
        filename=original_filename,
        file_type=parsed_doc.file_type,
        file_path=str(saved_file_path),
        file_size=file_size,
        page_count=parsed_doc.page_count,
        document_type=clean_type,
        jurisdiction="Unspecified",
        language="English",
        status="uploaded",
        content_hash=content_hash
    )
    db.add(new_doc)
    db.commit()

    # Save parsed pages
    for p in parsed_doc.pages:
        page_rec = Page(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            page_number=p.page_number,
            text=p.text
        )
        db.add(page_rec)
    db.commit()
    db.refresh(new_doc)

    return DocumentMetadataResponse.model_validate(new_doc)

@router.get("", response_model=List[DocumentMetadataResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Allow demo user to see demo documents as well
    if current_user.is_demo:
        docs = db.query(Document).filter(
            (Document.user_id == current_user.id) | (Document.user_id == "demo-user-lexlens")
        ).order_by(Document.created_at.desc()).all()
    else:
        docs = db.query(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc()).all()
    return [DocumentMetadataResponse.model_validate(d) for d in docs]

@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = verify_document_ownership(document_id, current_user, db)
    
    # Sub-millisecond LRU cache lookup for full document intelligence
    cache_key = f"{current_user.id}:{document_id}:{doc.updated_at.isoformat() if doc.updated_at else ''}"
    cached = document_cache.get(cache_key)
    if cached is not None:
        return cached

    # Build analysis response if analyzed
    analysis_resp = None
    if doc.status == "analyzed":
        analysis_resp = FullAnalysisResponse(
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

    res = DocumentDetailResponse(
        id=doc.id,
        user_id=doc.user_id,
        title=doc.title,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        page_count=doc.page_count,
        document_type=doc.document_type,
        jurisdiction=doc.jurisdiction,
        language=doc.language,
        status=doc.status,
        error_message=doc.error_message,
        summary=doc.summary,
        uploaded_at=doc.uploaded_at,
        created_at=doc.created_at,
        pages=[{"id": p.id, "page_number": p.page_number, "text": p.text} for p in sorted(doc.pages, key=lambda x: x.page_number)],
        analysis=analysis_resp
    )
    document_cache.set(cache_key, res)
    return res

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = verify_document_ownership(document_id, current_user, db)
    # Invalidate cache
    document_cache.delete(f"{current_user.id}:{document_id}")
    query_cache.clear()

    # Delete file from storage if exists
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return {"status": "success", "message": f"Document {document_id} and associated legal intelligence successfully deleted."}
