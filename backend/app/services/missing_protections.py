import re
from typing import List, Dict, Any

class MissingProtectionAuditor:
    @staticmethod
    def audit_document(
        clauses: List[Dict[str, Any]],
        full_text: str,
        document_type: str = "general_contract"
    ) -> List[Dict[str, Any]]:
        findings = []
        lower_text = full_text.lower()
        clause_categories = {c.get("category", "") for c in clauses}

        # 1. Limitation of Liability / Liability Cap Check
        has_liability_cap = False
        if "limitation of liability" in lower_text or "liability cap" in lower_text or "shall not exceed" in lower_text:
            has_liability_cap = True
        
        if not has_liability_cap:
            findings.append({
                "protection_type": "Limitation of Liability Cap",
                "description": "No clearly identified liability cap or aggregate financial ceiling was found in the analyzed document.",
                "recommendation": "Consider consulting a legal professional regarding adding an explicit cap on aggregate damages (e.g., limited to fees paid in preceding 12 months).",
                "severity": "High"
            })

        # 2. Pre-existing IP Carveout (especially important for Employment & Vendor agreements)
        if document_type in ["employment_agreement", "vendor_contract", "general_contract"]:
            has_ip_assignment = "intellectual property" in lower_text or "inventions" in lower_text or "work made for hire" in lower_text
            has_ip_exclusion = "pre-existing" in lower_text or "prior inventions" in lower_text or "schedule of excluded" in lower_text
            if has_ip_assignment and not has_ip_exclusion:
                findings.append({
                    "protection_type": "Pre-Existing IP Carve-Out",
                    "description": "Broad intellectual property assignment was identified, but no clearly identified carve-out or schedule for pre-existing personal IP was found in the analyzed document.",
                    "recommendation": "Review whether prior inventions, personal open-source projects, or pre-existing proprietary tools should be explicitly scheduled and excluded from transfer.",
                    "severity": "Significant"
                })

        # 3. Mutual Confidentiality Protection
        if "confidential" in lower_text:
            is_unilateral = ("employee shall hold" in lower_text or "vendor shall keep" in lower_text or "recipient agrees" in lower_text) and not ("mutual" in lower_text or "each party agrees" in lower_text or "both parties" in lower_text)
            if is_unilateral:
                findings.append({
                    "protection_type": "Mutual Confidentiality Protection",
                    "description": "Confidentiality obligations appear to be one-sided; no clearly identified mutual confidentiality protection for your proprietary disclosures was found in the analyzed document.",
                    "recommendation": "Ask counsel if mutual confidentiality protection should be requested so both parties are equally bound.",
                    "severity": "Moderate"
                })

        # 4. Notice and Cure Period for Breach
        has_cure_period = "cure period" in lower_text or "cure such breach" in lower_text or "days to remedy" in lower_text
        has_termination_for_cause = "breach" in lower_text and "terminate" in lower_text
        if has_termination_for_cause and not has_cure_period:
            findings.append({
                "protection_type": "Notice and Opportunity to Cure",
                "description": "Termination for breach is provided, but no clearly identified written cure period (e.g., 15 or 30 days to remedy an alleged breach) was found in the analyzed document.",
                "recommendation": "Confirm whether a formal written notice and cure window should be required before termination for cause can be triggered.",
                "severity": "Moderate"
            })

        # 5. Dispute Resolution / Mediation Escalation Step
        has_dispute = "arbitration" in lower_text or "court" in lower_text or "litigation" in lower_text
        has_mediation = "mediation" in lower_text or "negotiate in good faith" in lower_text
        if has_dispute and not has_mediation:
            findings.append({
                "protection_type": "Informal Dispute Escalation / Mediation",
                "description": "Binding dispute resolution or litigation is specified, but no clearly identified informal executive negotiation or mediation step was found in the analyzed document.",
                "recommendation": "Consider adding an escalation step (e.g., 30-day good faith negotiation or non-binding mediation) before costly formal proceedings.",
                "severity": "Notice"
            })

        return findings
