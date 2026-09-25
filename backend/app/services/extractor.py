import json
import re
import logging
from typing import List, Dict, Any, Optional
from backend.app.services.ai_providers import AIProviderFactory
from backend.app.services.security import SecurityService

logger = logging.getLogger(__name__)

TAXONOMY_CATEGORIES = [
    "Confidentiality", "Termination", "Notice", "Payment", "Compensation",
    "Liability", "Indemnification", "Intellectual Property", "Non-compete",
    "Non-solicitation", "Data Protection", "Privacy", "Warranties",
    "Representations", "Dispute Resolution", "Arbitration", "Governing Law",
    "Renewal", "Automatic Renewal", "Force Majeure", "Assignment",
    "Insurance", "Compliance", "Miscellaneous"
]

EXTRACTION_SYSTEM_PROMPT = """You are LexLens, a precision legal intelligence extraction system.
Your mission is to parse legal document text and extract structured representations.

CORE INSTRUCTIONS:
1. Ground every claim directly in the provided text.
2. DO NOT hallucinate facts, dates, or obligations.
3. If an obligation or condition is ambiguous, set is_ambiguous=true and provide ambiguity_reason.
4. Extract exact clause numbers, parties, rights, restrictions, financial terms, and deadlines.
5. In plain_explanation, explain in simple, accessible terms for a non-lawyer without altering legal meaning.
6. In questions_to_ask, provide 2-3 specific, high-value questions the user should consider asking a lawyer.
7. Return ONLY valid JSON adhering strictly to the schema provided."""

class LegalExtractor:
    @staticmethod
    def extract_document_intelligence(
        full_text: str,
        pages_summary: List[Dict[str, Any]],
        document_filename: str
    ) -> Dict[str, Any]:
        """
        Executes structured extraction using Gemini 3.8 Flash with prompt injection defense,
        falling back to rule-based heuristic extraction if necessary.
        """
        # Wrap untrusted document content safely
        safe_context = SecurityService.wrap_untrusted_context(full_text[:35000])

        prompt = f"""Analyze the following legal document (File: '{document_filename}').
Extract the document metadata, parties, major clauses, obligations, rights, deadlines, restrictions, and financial terms.

DOCUMENT TEXT:
{safe_context}

Produce a JSON response with this exact structure:
{{
  "document_type": "employment_agreement" | "lease_agreement" | "vendor_contract" | "nda" | "general_contract",
  "jurisdiction": "State/Country or 'Unspecified'",
  "language": "English",
  "summary": "Concise 3-4 sentence plain-language executive summary of the agreement",
  "parties": [
    {{
      "name": "Acme Corp",
      "role": "Employer",
      "party_type": "Corporation"
    }}
  ],
  "clauses": [
    {{
      "clause_number": "4.1",
      "title": "Payment Terms",
      "text": "Full verbatim excerpt of clause...",
      "page_start": 1,
      "page_end": 1,
      "category": "Payment",
      "plain_explanation": "Client must pay invoices within 30 days of receipt.",
      "risk_note": "Ensure invoices are reviewed immediately upon receipt to meet the 30-day window.",
      "questions_to_ask": ["What happens if an invoice is disputed in good faith?"]
    }}
  ],
  "obligations": [
    {{
      "actor": "Employee",
      "action": "provide written notice prior to resignation",
      "target_object": "written resignation notice",
      "trigger": "voluntary resignation",
      "deadline": "90 days",
      "duration": "90 days",
      "condition": null,
      "is_ambiguous": false,
      "ambiguity_reason": null,
      "source_clause_number": "18.2",
      "source_page": 2,
      "excerpt": "Employee shall provide ninety (90) days prior written notice..."
    }}
  ],
  "rights": [
    {{
      "holder": "Employer",
      "right_text": "terminate employment without cause upon 30 days written notice",
      "condition": "payment of accrued compensation",
      "source_clause_number": "17.1",
      "source_page": 2,
      "excerpt": "Company may terminate this Agreement without cause..."
    }}
  ],
  "deadlines": [
    {{
      "event": "Resignation notice period",
      "duration_or_date": "90 days",
      "triggering_condition": "Employee resignation",
      "category": "Notice",
      "source_clause_number": "18.2",
      "source_page": 2
    }}
  ],
  "restrictions": [
    {{
      "restriction_type": "Non-compete",
      "restricted_party": "Employee",
      "activity": "Engaging in or advising competing enterprise software businesses",
      "duration": "12 months post-termination",
      "scope": "Within North America",
      "source_clause_number": "12.1",
      "source_page": 2
    }}
  ],
  "financial_terms": [
    {{
      "item": "Base Salary",
      "amount": "$165,000",
      "currency": "USD",
      "frequency": "Annual",
      "condition": "Subject to standard payroll deductions",
      "source_clause_number": "3.1"
    }}
  ]
}}"""

        llm = AIProviderFactory.get_llm_provider()
        try:
            result = llm.generate_json(prompt=prompt, system_instruction=EXTRACTION_SYSTEM_PROMPT)
            # Validate core keys
            required_keys = ["document_type", "summary", "parties", "clauses", "obligations"]
            if all(k in result for k in required_keys):
                return result
            else:
                logger.warning("LLM extraction missing required keys, applying heuristic supplementation.")
        except Exception as e:
            logger.error(f"LLM extraction error: {e}. Falling back to rule-based parser.")

        return LegalExtractor._heuristic_extraction(full_text, pages_summary, document_filename)

    @staticmethod
    def _heuristic_extraction(
        full_text: str,
        pages_summary: List[Dict[str, Any]],
        filename: str
    ) -> Dict[str, Any]:
        """
        Deterministic rule-based extractor for offline execution and fallback safety.
        """
        lower_text = full_text.lower()
        
        # Detect Document Type
        doc_type = "general_contract"
        if "employment" in lower_text or "employee" in lower_text or "salary" in lower_text:
            doc_type = "employment_agreement"
        elif "lease" in lower_text or "tenant" in lower_text or "landlord" in lower_text or "premises" in lower_text:
            doc_type = "lease_agreement"
        elif "vendor" in lower_text or "services agreement" in lower_text or "client" in lower_text:
            doc_type = "vendor_contract"
        elif "confidential" in lower_text or "non-disclosure" in lower_text:
            doc_type = "nda"

        # Detect Jurisdiction
        jurisdiction = "Unspecified"
        gov_match = re.search(r"governed\s+by\s+(?:the\s+laws\s+of\s+)?([A-Za-z\s]+?)(?:\.|\,|\;|\n)", full_text, re.IGNORECASE)
        if gov_match:
            jurisdiction = gov_match.group(1).strip()[:40]

        # Extract Parties
        parties = []
        party_match = re.findall(r"between\s+([A-Za-z0-9\s,\.]+?)\s+\([\"']([A-Za-z\s]+)[\"']\)\s+and\s+([A-Za-z0-9\s,\.]+?)\s+\([\"']([A-Za-z\s]+)[\"']\)", full_text, re.IGNORECASE)
        if party_match:
            p1_name, p1_role, p2_name, p2_role = party_match[0]
            parties.append({"name": p1_name.strip(), "role": p1_role.strip(), "party_type": "Corporation"})
            parties.append({"name": p2_name.strip(), "role": p2_role.strip(), "party_type": "Individual"})
        else:
            if doc_type == "employment_agreement":
                parties.append({"name": "Employing Company", "role": "Employer", "party_type": "Corporation"})
                parties.append({"name": "Employee Candidate", "role": "Employee", "party_type": "Individual"})
            else:
                parties.append({"name": "First Party", "role": "Disclosing Party / Provider", "party_type": "Entity"})
                parties.append({"name": "Second Party", "role": "Receiving Party / Client", "party_type": "Entity"})

        # Heuristic Clause Extraction
        clauses = []
        clause_blocks = re.split(r"\n(?=(?:Section|Clause|Article|[0-9]+\.[0-9]+|[0-9]+\.)\s+)", full_text)
        
        for idx, block in enumerate(clause_blocks[:25]):
            block = block.strip()
            if not block or len(block) < 30:
                continue
            lines = block.split("\n")
            header = lines[0].strip()
            
            # Category taxonomy match
            matched_cat = "Miscellaneous"
            for cat in TAXONOMY_CATEGORIES:
                if cat.lower() in block[:200].lower():
                    matched_cat = cat
                    break
            
            c_num_match = re.search(r"^(?:(?:Section|Clause|Article)\s+)?([0-9A-Z\.]+)", header)
            c_num = c_num_match.group(1) if c_num_match else f"§{idx+1}"
            
            clauses.append({
                "clause_number": c_num,
                "title": header[:60],
                "text": block[:1200],
                "page_start": 1,
                "page_end": 1,
                "category": matched_cat,
                "plain_explanation": f"Specifies terms regarding {matched_cat.lower()} between the parties.",
                "risk_note": f"Review provisions concerning {matched_cat.lower()} carefully with legal counsel.",
                "questions_to_ask": [f"Does this {matched_cat.lower()} clause align with standard industry protections?"]
            })

        # Heuristic Obligations
        obligations = []
        shall_matches = re.finditer(r"([A-Z][a-z]+)\s+shall\s+([^\.\;\n]{10,140})", full_text)
        for m in list(shall_matches)[:12]:
            actor = m.group(1)
            action = m.group(2).strip()
            
            # Detect deadline keywords
            dl_match = re.search(r"within\s+(\d+\s+(?:days|months|hours|weeks))", action, re.IGNORECASE)
            dl_val = dl_match.group(1) if dl_match else None
            
            obligations.append({
                "actor": actor,
                "action": f"shall {action}",
                "target_object": None,
                "trigger": None,
                "deadline": dl_val,
                "duration": dl_val,
                "condition": None,
                "is_ambiguous": False,
                "ambiguity_reason": None,
                "source_clause_number": "General",
                "source_page": 1,
                "excerpt": m.group(0)[:180]
            })

        # Heuristic Deadlines
        deadlines = []
        dl_matches = re.finditer(r"(\d+)\s*(days|months|hours|weeks|business days)", full_text, re.IGNORECASE)
        seen_dls = set()
        for m in list(dl_matches)[:8]:
            val = m.group(0)
            if val.lower() not in seen_dls:
                seen_dls.add(val.lower())
                deadlines.append({
                    "event": f"Requirement within {val}",
                    "duration_or_date": val,
                    "triggering_condition": "Notice or triggering event",
                    "category": "Notice" if "day" in val else "Duration",
                    "source_clause_number": "General",
                    "source_page": 1
                })

        # Financial Terms
        financial_terms = []
        currency_matches = re.finditer(r"(\$\s*[0-9,]+(?:\.[0-9]{2})?|\b[0-9,]+\s*(?:USD|EUR|GBP|Dollars))", full_text)
        for m in list(currency_matches)[:6]:
            financial_terms.append({
                "item": "Payment / Fee / Compensation",
                "amount": m.group(0).strip(),
                "currency": "USD",
                "frequency": "Periodic",
                "condition": None,
                "source_clause_number": "Payment"
            })

        return {
            "document_type": doc_type,
            "jurisdiction": jurisdiction,
            "language": "English",
            "summary": f"A legally structured {doc_type.replace('_', ' ').title()} defining operational covenants, rights, and responsibilities between the identified parties.",
            "parties": parties,
            "clauses": clauses,
            "obligations": obligations,
            "rights": [],
            "deadlines": deadlines,
            "restrictions": [],
            "financial_terms": financial_terms
        }
