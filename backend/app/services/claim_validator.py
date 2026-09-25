import re
from typing import List, Dict, Any, Tuple
from backend.app.schemas.qa import Citation

class ClaimValidator:
    @staticmethod
    def validate_answer(
        answer: str,
        retrieved_chunks: List[Dict[str, Any]],
        document_title: str
    ) -> Tuple[List[Citation], List[str], float]:
        """
        Validates the generated claims against retrieved evidence chunks.
        Returns:
            citations: List of structured Citation objects
            unsupported_claims: List of identified unverified claims
            groundedness_score: Float between 0.0 and 1.0
        """
        citations: List[Citation] = []
        unsupported_claims: List[str] = []
        
        combined_evidence = " ".join([c["text"].lower() for c in retrieved_chunks])
        
        # 1. Build Citations from retrieved chunks
        for c in retrieved_chunks:
            clause_label = c.get("clause_id") or c.get("section") or "Relevant Provision"
            page_num = c.get("page_number", 1)
            raw_text = c.get("text", "")
            
            # Extract most relevant sentence as excerpt
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw_text) if len(s.strip()) > 20]
            short_excerpt = sentences[0][:200] if sentences else raw_text[:150]
            
            citations.append(Citation(
                document_name=document_title,
                clause_number=str(clause_label),
                page_number=page_num,
                excerpt=short_excerpt
            ))

        # 2. Check for numeric and deadline claims in the answer
        # e.g., '90 days', '$150,000', '12 months', 'Clause 18.2'
        claims_checked = 0
        claims_grounded = 0

        # Numbers and durations:
        duration_claims = re.findall(r"\b(\d+)\s+(?:days|months|years|weeks|hours|business days)\b", answer, re.IGNORECASE)
        for dur in duration_claims:
            claims_checked += 1
            if dur in combined_evidence:
                claims_grounded += 1
            else:
                unsupported_claims.append(f"Specified timeframe '{dur}' not verified in retrieved document evidence.")

        # Monetary figures:
        money_claims = re.findall(r"\$\s*([0-9,]+)", answer)
        for m in money_claims:
            claims_checked += 1
            clean_m = m.replace(",", "")
            if clean_m in combined_evidence or m in combined_evidence:
                claims_grounded += 1
            else:
                unsupported_claims.append(f"Financial figure '${m}' not corroborated by retrieved text.")

        # Definitive legal judgment claims warning:
        unsubstantiated_keywords = ["is illegal", "is void", "is strictly forbidden by law", "court will definitely"]
        for kw in unsubstantiated_keywords:
            if kw in answer.lower():
                claims_checked += 1
                unsupported_claims.append(f"Definitive legal conclusion '{kw}' made without statutory grounding.")

        # Compute groundedness score
        if claims_checked == 0:
            groundedness_score = 1.0
        else:
            groundedness_score = round(max(0.0, claims_grounded / claims_checked), 2)

        return citations, unsupported_claims, groundedness_score
