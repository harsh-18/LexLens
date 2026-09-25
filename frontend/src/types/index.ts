export interface DocumentMetadata {
  id: string;
  user_id: string;
  title: string;
  filename: string;
  file_type: string;
  file_size: number;
  page_count: number;
  document_type: string;
  jurisdiction: string;
  language: string;
  status: 'uploaded' | 'processing' | 'analyzed' | 'failed';
  error_message?: string;
  summary?: string;
  uploaded_at: string;
  created_at: string;
}

export interface DocumentPage {
  id: string;
  page_number: number;
  text: string;
}

export interface Party {
  id?: string;
  name: string;
  role: string;
  party_type: string;
}

export interface Clause {
  id?: string;
  clause_number?: string;
  title?: string;
  text: string;
  page_start: number;
  page_end: number;
  category: string;
  plain_explanation?: string;
  risk_note?: string;
  questions_to_ask?: string;
}

export interface Obligation {
  id?: string;
  actor: string;
  action: string;
  target_object?: string;
  trigger?: string;
  deadline?: string;
  duration?: string;
  condition?: string;
  is_ambiguous: boolean;
  ambiguity_reason?: string;
  source_clause_number?: string;
  source_page: number;
  excerpt?: string;
}

export interface RightItem {
  id?: string;
  holder: string;
  right_text: string;
  condition?: string;
  source_clause_number?: string;
  source_page: number;
  excerpt?: string;
}

export interface DeadlineItem {
  id?: string;
  event: string;
  duration_or_date: string;
  triggering_condition?: string;
  category: string;
  order_index: number;
  source_clause_number?: string;
  source_page: number;
}

export interface RestrictionItem {
  id?: string;
  restriction_type: string;
  restricted_party: string;
  activity: string;
  duration?: string;
  scope?: string;
  source_clause_number?: string;
  source_page: number;
}

export interface FinancialTerm {
  id?: string;
  item: string;
  amount: string;
  currency: string;
  frequency?: string;
  condition?: string;
  source_clause_number?: string;
}

export interface Contradiction {
  id?: string;
  title: string;
  clause_a: string;
  text_a: string;
  page_a: number;
  clause_b: string;
  text_b: string;
  page_b: number;
  explanation: string;
  severity: string;
}

export interface MissingProtection {
  id?: string;
  protection_type: string;
  description: string;
  recommendation: string;
  severity: string;
}

export interface FullAnalysis {
  document_id: string;
  title: string;
  document_type: string;
  jurisdiction: string;
  language: string;
  summary?: string;
  page_count: number;
  parties: Party[];
  clauses: Clause[];
  obligations: Obligation[];
  rights: RightItem[];
  deadlines: DeadlineItem[];
  restrictions: RestrictionItem[];
  financial_terms: FinancialTerm[];
  contradictions: Contradiction[];
  missing_protections: MissingProtection[];
}

export interface DocumentDetail extends DocumentMetadata {
  pages: DocumentPage[];
  analysis?: FullAnalysis;
}

export interface Citation {
  document_name: string;
  clause_number: string;
  page_number: number;
  excerpt: string;
}

export interface QAResponse {
  question: string;
  answer: string;
  citations: Citation[];
  unsupported_claims: string[];
  is_grounded: boolean;
  groundedness_score: number;
  latency_ms: number;
  token_usage: number;
}

export interface ComparisonRow {
  topic: string;
  version_a_value: string;
  version_b_value: string;
  significance: string;
  analysis: string;
}

export interface ClauseDiff {
  clause_identifier: string;
  status: 'Added' | 'Removed' | 'Modified' | 'Unchanged';
  title: string;
  version_a_text?: string;
  version_b_text?: string;
  change_summary: string;
}

export interface ComparisonResponse {
  document_a_id: string;
  document_a_title: string;
  document_b_id: string;
  document_b_title: string;
  executive_summary: string;
  key_differences_table: ComparisonRow[];
  clause_diffs: ClauseDiff[];
  obligation_changes: string[];
  deadline_changes: string[];
  financial_changes: string[];
  significant_risk_changes: string[];
}

export interface LawyerQuestion {
  category: string;
  question: string;
  context_clause?: string;
  priority: string;
}

export interface ConsultationBriefResponse {
  document_id: string;
  document_title: string;
  document_type: string;
  prepared_date: string;
  executive_overview: string;
  relevant_facts: string[];
  critical_clauses_to_review: string[];
  potential_issues_and_risks: string[];
  unanswered_questions: string[];
  questions_for_counsel: LawyerQuestion[];
  documents_to_gather: string[];
  action_timeline: string[];
  disclaimer: string;
}

export interface TestCaseResult {
  test_id: string;
  category: string;
  name: string;
  passed: boolean;
  groundedness: number;
  citation_precision: number;
  unsupported_claims_detected: number;
  latency_ms: number;
  notes?: string;
}

export interface EvaluationReportResponse {
  evaluation_id: string;
  timestamp: string;
  overall_score: number;
  groundedness_score: number;
  citation_coverage: number;
  unsupported_claim_rate: number;
  avg_latency_ms: number;
  total_tests: number;
  passed_tests: number;
  results: TestCaseResult[];
}
