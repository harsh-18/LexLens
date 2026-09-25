from datetime import datetime
import logging
from typing import Dict, Any, List
from backend.app.schemas.consultation import ConsultationBriefResponse, LawyerQuestion
from backend.app.services.ai_providers import AIProviderFactory

logger = logging.getLogger(__name__)

CONSULTATION_PROMPT = """You are LexLens Legal Consultation Preparation Assistant.
Based on the analyzed legal agreement below, prepare a structured, high-efficiency consultation brief for the client to bring to their attorney meeting.

DOCUMENT INFO:
Title: {title}
Type: {doc_type}
Jurisdiction: {jurisdiction}
Summary: {summary}

KEY CLAUSES & ATTENTION AREAS:
{clauses_overview}

POTENTIAL CONTRADICTIONS:
{contradictions_overview}

MISSING PROTECTIONS:
{missing_protections_overview}

Generate a comprehensive brief in JSON format:
{{
  "executive_overview": "A concise briefing on the transaction or employment relationship, its stage, and core risks...",
  "relevant_facts": [
    "Key party names and roles",
    "Effective dates or proposed start dates",
    "Total compensation or financial commitment"
  ],
  "critical_clauses_to_review": [
    "Clause 12: Broad IP assignment covering off-duty inventions",
    "Clause 18: 90-day pre-resignation notice requirement"
  ],
  "potential_issues_and_risks": [
    "Inconsistent notice periods between Clause 5 and Clause 18",
    "Absence of clearly defined pre-existing IP carve-out"
  ],
  "unanswered_questions": [
    "Does employer enforce non-competes in California/relevant state?",
    "Are freelance side projects included under assignment terms?"
  ],
  "questions_for_counsel": [
    {{
      "category": "Intellectual Property",
      "question": "Can we strike or narrow Clause 12 to explicitly exclude open-source projects created on personal equipment?",
      "context_clause": "Clause 12.3",
      "priority": "High"
    }},
    {{
      "category": "Termination & Notice",
      "question": "Is the 90-day resignation notice period customary, and what happens if I need to leave sooner?",
      "context_clause": "Clause 18.2",
      "priority": "High"
    }}
  ],
  "documents_to_gather": [
    "List of pre-existing patents, code repositories, or inventions to attach as Exhibit A",
    "Prior offer letter or communications regarding compensation and remote work"
  ],
  "action_timeline": [
    "Immediate: Review flagged contradiction in payment/notice clauses",
    "Prior to consultation: Gather Exhibit A inventory of pre-existing work",
    "Post-consultation: Deliver redline markups to drafting party"
  ]
}}"""

class ConsultationBriefService:
    @staticmethod
    def generate_brief(doc_dict: Dict[str, Any]) -> ConsultationBriefResponse:
        title = doc_dict.get("title", "Legal Document")
        doc_type = doc_dict.get("document_type", "general_contract")
        jurisdiction = doc_dict.get("jurisdiction", "Unspecified")
        summary = doc_dict.get("summary", "")
        
        # Format overviews
        clauses = doc_dict.get("clauses", [])
        clauses_overview = "\n".join([
            f"- [{c.get('clause_number', '§')} - {c.get('category', 'Category')}]: {c.get('plain_explanation') or c.get('text', '')[:180]}"
            for c in clauses[:10]
        ])
        
        contradictions = doc_dict.get("contradictions", [])
        contradictions_overview = "\n".join([
            f"- Conflict: {c.get('title')}: {c.get('clause_a')} vs {c.get('clause_b')}. Explanation: {c.get('explanation')}"
            for c in contradictions
        ]) or "None identified."
        
        missing = doc_dict.get("missing_protections", [])
        missing_overview = "\n".join([
            f"- Missing Protection: {m.get('protection_type')}. {m.get('description')}"
            for m in missing
        ]) or "None flagged."

        try:
            llm = AIProviderFactory.get_llm_provider()
            prompt = CONSULTATION_PROMPT.format(
                title=title,
                doc_type=doc_type,
                jurisdiction=jurisdiction,
                summary=summary,
                clauses_overview=clauses_overview,
                contradictions_overview=contradictions_overview,
                missing_protections_overview=missing_overview
            )
            data = llm.generate_json(prompt)
            
            questions = [
                LawyerQuestion(
                    category=q.get("category", "General"),
                    question=q.get("question", ""),
                    context_clause=q.get("context_clause"),
                    priority=q.get("priority", "High")
                )
                for q in data.get("questions_for_counsel", [])
            ]
            
            return ConsultationBriefResponse(
                document_id=doc_dict.get("id", "doc"),
                document_title=title,
                document_type=doc_type,
                prepared_date=datetime.utcnow().strftime("%B %d, %Y"),
                executive_overview=data.get("executive_overview", summary),
                relevant_facts=data.get("relevant_facts", []),
                critical_clauses_to_review=data.get("critical_clauses_to_review", []),
                potential_issues_and_risks=data.get("potential_issues_and_risks", []),
                unanswered_questions=data.get("unanswered_questions", []),
                questions_for_counsel=questions,
                documents_to_gather=data.get("documents_to_gather", []),
                action_timeline=data.get("action_timeline", [])
            )
        except Exception as e:
            logger.warning(f"Consultation brief LLM fallback: {e}")
            
            # Deterministic fallback brief
            fallback_questions = [
                LawyerQuestion(
                    category="Obligations & Deadlines",
                    question="Are the extracted notice windows and obligations standard for this type of agreement?",
                    context_clause="General Terms",
                    priority="High"
                ),
                LawyerQuestion(
                    category="Liability & Risk",
                    question="Does the agreement adequately protect against uncapped liability or unilateral breach?",
                    context_clause="Liability",
                    priority="High"
                )
            ]
            return ConsultationBriefResponse(
                document_id=doc_dict.get("id", "doc"),
                document_title=title,
                document_type=doc_type,
                prepared_date=datetime.utcnow().strftime("%B %d, %Y"),
                executive_overview=f"Automated consultation preparation for {title}. Summary: {summary}",
                relevant_facts=[
                    f"Document Type: {doc_type}",
                    f"Jurisdiction: {jurisdiction}",
                    f"Identified Clauses: {len(clauses)}"
                ],
                critical_clauses_to_review=[c.get("clause_number", "Clause") for c in clauses[:5]],
                potential_issues_and_risks=[c.get("title", "Conflict") for c in contradictions] + [m.get("protection_type", "Notice") for m in missing],
                unanswered_questions=["Confirm governing law applicability and any ambiguous obligations flagged."],
                questions_for_counsel=fallback_questions,
                documents_to_gather=["Executed counterparts", "All exhibits and referenced schedules"],
                action_timeline=["Schedule attorney meeting", "Clarify contradictory terms before signing"]
            )
