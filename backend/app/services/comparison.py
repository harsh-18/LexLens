import logging
from typing import List, Dict, Any, Optional
from backend.app.schemas.comparison import ComparisonResponse, ComparisonRow, ClauseDiff
from backend.app.services.ai_providers import AIProviderFactory

logger = logging.getLogger(__name__)

COMPARISON_PROMPT = """You are LexLens Contract Version Comparison Specialist.
Analyze the differences between Version A and Version B of this legal agreement.

VERSION A SUMMARY & KEY TERMS:
Title: {title_a}
{summary_a}

VERSION B SUMMARY & KEY TERMS:
Title: {title_b}
{summary_b}

Generate a structured JSON comparison detailing:
1. An executive summary of what changed.
2. A comparison table of key topics (Notice period, Payment terms, Liability, Governing law/Dispute resolution, Non-compete scope, Compensation).
3. Specific obligation changes.
4. Specific deadline changes.
5. Specific financial changes.
6. Significant risk shifts.

Output JSON format:
{{
  "executive_summary": "Executive summary of material shifts between the versions...",
  "key_differences_table": [
    {{
      "topic": "Notice Period",
      "version_a_value": "30 days",
      "version_b_value": "90 days",
      "significance": "Critical",
      "analysis": "Version B triples the notice period required prior to resignation."
    }},
    {{
      "topic": "Payment Terms",
      "version_a_value": "Net 30 days",
      "version_b_value": "Net 60 days",
      "significance": "Notable",
      "analysis": "Version B extends the client payment window by 30 additional days."
    }}
  ],
  "obligation_changes": ["Employee notice obligation increased from 30 to 90 days."],
  "deadline_changes": ["Invoice payment window shifted from 30 to 60 days."],
  "financial_changes": ["Base compensation adjusted from $150,000 to $165,000."],
  "significant_risk_changes": ["Non-compete geographic scope expanded from local county to North America."]
}}"""

class ContractComparator:
    @staticmethod
    def compare_documents(doc_a_dict: Dict[str, Any], doc_b_dict: Dict[str, Any]) -> ComparisonResponse:
        title_a = doc_a_dict.get("title", "Version A")
        title_b = doc_b_dict.get("title", "Version B")
        
        # Build clause diffs
        clauses_a = {c.get("clause_number", f"§{idx}"): c for idx, c in enumerate(doc_a_dict.get("clauses", []))}
        clauses_b = {c.get("clause_number", f"§{idx}"): c for idx, c in enumerate(doc_b_dict.get("clauses", []))}
        
        clause_diffs: List[ClauseDiff] = []
        all_keys = set(clauses_a.keys()).union(set(clauses_b.keys()))
        
        for k in sorted(all_keys):
            ca = clauses_a.get(k)
            cb = clauses_b.get(k)
            if ca and not cb:
                clause_diffs.append(ClauseDiff(
                    clause_identifier=k,
                    status="Removed",
                    title=ca.get("title", "Clause"),
                    version_a_text=ca.get("text", "")[:300],
                    version_b_text=None,
                    change_summary="Clause was present in Version A but removed in Version B."
                ))
            elif cb and not ca:
                clause_diffs.append(ClauseDiff(
                    clause_identifier=k,
                    status="Added",
                    title=cb.get("title", "Clause"),
                    version_a_text=None,
                    version_b_text=cb.get("text", "")[:300],
                    change_summary="New clause introduced in Version B."
                ))
            else:
                # Both exist - compare text
                text_a = ca.get("text", "").strip()
                text_b = cb.get("text", "").strip()
                if text_a != text_b:
                    clause_diffs.append(ClauseDiff(
                        clause_identifier=k,
                        status="Modified",
                        title=cb.get("title", ca.get("title", "Clause")),
                        version_a_text=text_a[:300],
                        version_b_text=text_b[:300],
                        change_summary=f"Wording or parameters modified in {k}."
                    ))
                else:
                    clause_diffs.append(ClauseDiff(
                        clause_identifier=k,
                        status="Unchanged",
                        title=ca.get("title", "Clause"),
                        version_a_text=text_a[:200],
                        version_b_text=text_b[:200],
                        change_summary="Identical wording preserved."
                    ))

        # Attempt AI Comparison Synthesis
        try:
            llm = AIProviderFactory.get_llm_provider()
            prompt = COMPARISON_PROMPT.format(
                title_a=title_a,
                summary_a=doc_a_dict.get("summary", ""),
                title_b=title_b,
                summary_b=doc_b_dict.get("summary", "")
            )
            ai_data = llm.generate_json(prompt)
            
            table_rows = [
                ComparisonRow(
                    topic=r.get("topic", "Topic"),
                    version_a_value=r.get("version_a_value", "-"),
                    version_b_value=r.get("version_b_value", "-"),
                    significance=r.get("significance", "Notable"),
                    analysis=r.get("analysis", "")
                )
                for r in ai_data.get("key_differences_table", [])
            ]
            
            return ComparisonResponse(
                document_a_id=doc_a_dict.get("id", "doc_a"),
                document_a_title=title_a,
                document_b_id=doc_b_dict.get("id", "doc_b"),
                document_b_title=title_b,
                executive_summary=ai_data.get("executive_summary", "Comparison of material terms between document versions."),
                key_differences_table=table_rows,
                clause_diffs=clause_diffs,
                obligation_changes=ai_data.get("obligation_changes", []),
                deadline_changes=ai_data.get("deadline_changes", []),
                financial_changes=ai_data.get("financial_changes", []),
                significant_risk_changes=ai_data.get("significant_risk_changes", [])
            )
        except Exception as e:
            logger.warning(f"AI comparison fallback due to: {e}")
            
            # Deterministic fallback comparison
            fallback_rows = [
                ComparisonRow(
                    topic="Document Structure & Scope",
                    version_a_value=f"{len(doc_a_dict.get('clauses', []))} clauses",
                    version_b_value=f"{len(doc_b_dict.get('clauses', []))} clauses",
                    significance="Notable",
                    analysis="Change in total articulated clauses between versions."
                )
            ]
            return ComparisonResponse(
                document_a_id=doc_a_dict.get("id", "doc_a"),
                document_a_title=title_a,
                document_b_id=doc_b_dict.get("id", "doc_b"),
                document_b_title=title_b,
                executive_summary="Automated clause-level differential analysis between document versions.",
                key_differences_table=fallback_rows,
                clause_diffs=clause_diffs,
                obligation_changes=[f"Modified {len([d for d in clause_diffs if d.status == 'Modified'])} clauses between versions."],
                deadline_changes=["Review modified notice and payment windows in the clause diffs table."],
                financial_changes=["Check financial terms section for updated compensation or fee schedules."],
                significant_risk_changes=["Consult counsel regarding any modified restrictive covenants or liability allocations."]
            )
