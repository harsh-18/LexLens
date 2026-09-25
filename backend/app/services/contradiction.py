import re
import logging
from typing import List, Dict, Any
from backend.app.services.ai_providers import AIProviderFactory
from backend.app.services.security import SecurityService

logger = logging.getLogger(__name__)

CONTRADICTION_PROMPT = """You are LexLens Contradiction Detection Engine.
Analyze the following clauses from a legal agreement and identify any POTENTIAL CONTRADICTIONS, CONFLICTS, OR INCONSISTENCIES between them.

Examples of inconsistencies to look for:
1. Different payment or invoice deadlines (e.g., 30 days in Clause 4 vs 60 days in Schedule B).
2. Conflicting termination notice periods (e.g., 30 days in one section vs 90 days in another).
3. Conflicting governing law, dispute resolution, or arbitration forums.
4. Conflicting cure periods (e.g., 10 days vs 30 days).
5. Conflicting liability caps or exclusions.

CLAUSES EXTRACTED:
{clauses_text}

Output JSON format:
{{
  "contradictions": [
    {{
      "title": "Inconsistent Payment Terms",
      "clause_a": "Clause 4.1",
      "text_a": "Invoices payable within 30 days...",
      "page_a": 1,
      "clause_b": "Schedule B",
      "text_b": "Payment due within 60 days of invoice receipt...",
      "page_b": 3,
      "explanation": "These provisions appear to specify different payment periods. The agreement should be reviewed to determine whether one provision takes precedence.",
      "severity": "Significant"
    }}
  ]
}}
If no genuine contradictions exist, return {{"contradictions": []}}."""

class ContradictionDetector:
    @staticmethod
    def detect_contradictions(clauses: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        # First, run rule-based cross checks for classic legal contract inconsistencies
        rule_findings = ContradictionDetector._detect_rule_based_inconsistencies(clauses, full_text)
        
        # Second, run LLM cross-checking if clauses are present
        if len(clauses) >= 2:
            try:
                llm = AIProviderFactory.get_llm_provider()
                clauses_summary = "\n\n".join([
                    f"[{c.get('clause_number', 'Clause')}] Page {c.get('page_start', 1)}: {c.get('text', '')[:400]}"
                    for c in clauses[:15]
                ])
                safe_context = SecurityService.wrap_untrusted_context(clauses_summary)
                prompt = CONTRADICTION_PROMPT.format(clauses_text=safe_context)
                res = llm.generate_json(prompt)
                llm_contradictions = res.get("contradictions", [])
                
                # Combine without duplicates
                seen_titles = {r["title"].lower() for r in rule_findings}
                for item in llm_contradictions:
                    if item.get("title", "").lower() not in seen_titles:
                        rule_findings.append(item)
            except Exception as e:
                logger.warning(f"LLM contradiction check skipped/failed: {e}")

        return rule_findings

    @staticmethod
    def _detect_rule_based_inconsistencies(clauses: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        findings = []

        # 1. Notice period discrepancy check (e.g. 30 days vs 90 days notice)
        notice_days = []
        for c in clauses:
            t = c.get("text", "")
            matches = re.finditer(r"(?:[a-z\-]+\s*)?(?:\()?\b(\d+)\b(?:\))?\s*(?:calendar\s+|business\s+)?days['\"]?\s+(?:prior\s+written\s+)?notice", t, re.IGNORECASE)
            for m in matches:
                days = int(m.group(1))
                notice_days.append({
                    "days": days,
                    "clause": c.get("clause_number", "Notice Clause"),
                    "text": t[:250],
                    "page": c.get("page_start", 1)
                })

        if len(notice_days) >= 2:
            unique_days = {n["days"] for n in notice_days}
            if len(unique_days) > 1:
                sorted_notices = sorted(notice_days, key=lambda x: x["days"])
                n1, n2 = sorted_notices[0], sorted_notices[-1]
                findings.append({
                    "title": "Discrepancy in Notice Periods",
                    "clause_a": str(n1["clause"]),
                    "text_a": n1["text"],
                    "page_a": n1["page"],
                    "clause_b": str(n2["clause"]),
                    "text_b": n2["text"],
                    "page_b": n2["page"],
                    "explanation": f"The document specifies conflicting notice periods ({n1['days']} days in {n1['clause']} versus {n2['days']} days in {n2['clause']}). One provision may govern specific termination scenarios, or this may represent an inconsistency requiring legal clarification.",
                    "severity": "Significant"
                })

        # 2. Payment terms discrepancy check (e.g. 30 days vs 60 days)
        payment_windows = []
        for c in clauses:
            t = c.get("text", "")
            matches = re.finditer(r"(?:within|net|due\s+within)\s+(?:[a-z\-]+\s*)?(?:\()?\b(\d+)\b(?:\))?\s*(?:calendar\s+|business\s+)?days\s+(?:of|from|after)\s+(?:receipt|invoice|billing)", t, re.IGNORECASE)
            for m in matches:
                days = int(m.group(1))
                payment_windows.append({
                    "days": days,
                    "clause": c.get("clause_number", "Payment Clause"),
                    "text": t[:250],
                    "page": c.get("page_start", 1)
                })

        if len(payment_windows) >= 2:
            unique_windows = {p["days"] for p in payment_windows}
            if len(unique_windows) > 1:
                p1, p2 = payment_windows[0], payment_windows[-1]
                findings.append({
                    "title": "Conflicting Payment Periods",
                    "clause_a": str(p1["clause"]),
                    "text_a": p1["text"],
                    "page_a": p1["page"],
                    "clause_b": str(p2["clause"]),
                    "text_b": p2["text"],
                    "page_b": p2["page"],
                    "explanation": f"The agreement references different payment terms ({p1['days']} days vs {p2['days']} days). A legal professional should confirm whether one schedule supersedes the general terms.",
                    "severity": "Significant"
                })

        return findings
