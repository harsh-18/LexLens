from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from backend.app.schemas.legal import FullAnalysisResponse

class DocumentMetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    filename: str
    file_type: str
    file_size: int
    page_count: int
    document_type: str
    jurisdiction: str
    language: str
    status: str
    error_message: Optional[str] = None
    summary: Optional[str] = None
    uploaded_at: datetime
    created_at: datetime

class DocumentPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page_number: int
    text: str

class DocumentDetailResponse(DocumentMetadataResponse):
    pages: List[DocumentPageResponse] = []
    analysis: Optional[FullAnalysisResponse] = None
