from pydantic import BaseModel
from typing import List, Optional

class LawyerQuestion(BaseModel):
    category: str
    question: str
    context_clause: Optional[str] = None
    priority: str = "High"

class ConsultationBriefResponse(BaseModel):
    document_id: str
    document_title: str
    document_type: str
    prepared_date: str
    executive_overview: str
    relevant_facts: List[str] = []
    critical_clauses_to_review: List[str] = []
    potential_issues_and_risks: List[str] = []
    unanswered_questions: List[str] = []
    questions_for_counsel: List[LawyerQuestion] = []
    documents_to_gather: List[str] = []
    action_timeline: List[str] = []
    disclaimer: str = (
        "CONFIDENTIAL & INFORMATIONAL PREPARATION BRIEF: Prepared by LexLens for client consultation preparation. "
        "This document is for information and preparation purposes only and does NOT constitute professional legal advice."
    )
