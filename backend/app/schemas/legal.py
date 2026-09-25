from pydantic import BaseModel
from typing import Optional, List

class PartySchema(BaseModel):
    id: Optional[str] = None
    name: str
    role: str
    party_type: str = "Entity"

    class Config:
        from_attributes = True

class ClauseSchema(BaseModel):
    id: Optional[str] = None
    clause_number: Optional[str] = None
    title: Optional[str] = None
    text: str
    page_start: int = 1
    page_end: int = 1
    category: str = "Miscellaneous"
    plain_explanation: Optional[str] = None
    risk_note: Optional[str] = None
    questions_to_ask: Optional[str] = None

    class Config:
        from_attributes = True

class ObligationSchema(BaseModel):
    id: Optional[str] = None
    actor: str
    action: str
    target_object: Optional[str] = None
    trigger: Optional[str] = None
    deadline: Optional[str] = None
    duration: Optional[str] = None
    condition: Optional[str] = None
    is_ambiguous: bool = False
    ambiguity_reason: Optional[str] = None
    source_clause_number: Optional[str] = None
    source_page: int = 1
    excerpt: Optional[str] = None

    class Config:
        from_attributes = True

class RightSchema(BaseModel):
    id: Optional[str] = None
    holder: str
    right_text: str
    condition: Optional[str] = None
    source_clause_number: Optional[str] = None
    source_page: int = 1
    excerpt: Optional[str] = None

    class Config:
        from_attributes = True

class DeadlineSchema(BaseModel):
    id: Optional[str] = None
    event: str
    duration_or_date: str
    triggering_condition: Optional[str] = None
    category: str = "Notice"
    order_index: int = 0
    source_clause_number: Optional[str] = None
    source_page: int = 1

    class Config:
        from_attributes = True

class RestrictionSchema(BaseModel):
    id: Optional[str] = None
    restriction_type: str
    restricted_party: str
    activity: str
    duration: Optional[str] = None
    scope: Optional[str] = None
    source_clause_number: Optional[str] = None
    source_page: int = 1

    class Config:
        from_attributes = True

class FinancialTermSchema(BaseModel):
    id: Optional[str] = None
    item: str
    amount: str
    currency: str = "USD"
    frequency: Optional[str] = None
    condition: Optional[str] = None
    source_clause_number: Optional[str] = None

    class Config:
        from_attributes = True

class ContradictionSchema(BaseModel):
    id: Optional[str] = None
    title: str
    clause_a: str
    text_a: str
    page_a: int = 1
    clause_b: str
    text_b: str
    page_b: int = 1
    explanation: str
    severity: str = "Moderate"

    class Config:
        from_attributes = True

class MissingProtectionSchema(BaseModel):
    id: Optional[str] = None
    protection_type: str
    description: str
    recommendation: str
    severity: str = "Notice"

    class Config:
        from_attributes = True

class FullAnalysisResponse(BaseModel):
    document_id: str
    title: str
    document_type: str
    jurisdiction: str
    language: str
    summary: Optional[str] = None
    page_count: int
    parties: List[PartySchema] = []
    clauses: List[ClauseSchema] = []
    obligations: List[ObligationSchema] = []
    rights: List[RightSchema] = []
    deadlines: List[DeadlineSchema] = []
    restrictions: List[RestrictionSchema] = []
    financial_terms: List[FinancialTermSchema] = []
    contradictions: List[ContradictionSchema] = []
    missing_protections: List[MissingProtectionSchema] = []
