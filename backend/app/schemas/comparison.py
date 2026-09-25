from pydantic import BaseModel
from typing import List, Optional

class ComparisonRow(BaseModel):
    topic: str
    version_a_value: str
    version_b_value: str
    significance: str  # Critical, Notable, Minor, None
    analysis: str

class ClauseDiff(BaseModel):
    clause_identifier: str
    status: str  # Modified, Added, Removed, Unchanged
    title: str
    version_a_text: Optional[str] = None
    version_b_text: Optional[str] = None
    change_summary: str

class ComparisonResponse(BaseModel):
    document_a_id: str
    document_a_title: str
    document_b_id: str
    document_b_title: str
    executive_summary: str
    key_differences_table: List[ComparisonRow] = []
    clause_diffs: List[ClauseDiff] = []
    obligation_changes: List[str] = []
    deadline_changes: List[str] = []
    financial_changes: List[str] = []
    significant_risk_changes: List[str] = []
