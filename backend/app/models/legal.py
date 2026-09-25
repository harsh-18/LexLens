from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Page(Base):
    __tablename__ = "pages"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    document = relationship("Document", back_populates="pages")

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, default=1)
    section = Column(String, default="General")
    clause_id = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    embedding_json = Column(Text, nullable=True)  # JSON-encoded float list for semantic vector retrieval

    document = relationship("Document", back_populates="chunks")

class Clause(Base):
    __tablename__ = "clauses"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    clause_number = Column(String, nullable=True)  # e.g., "18.2", "Clause 4", "Schedule B"
    title = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    page_start = Column(Integer, default=1)
    page_end = Column(Integer, default=1)
    category = Column(String, default="Miscellaneous")  # 23-category taxonomy
    plain_explanation = Column(Text, nullable=True)  # Plain-language explanation for non-lawyers
    risk_note = Column(Text, nullable=True)  # Attention area rationale
    questions_to_ask = Column(Text, nullable=True)  # JSON list of questions for counsel

    document = relationship("Document", back_populates="clauses")

class Party(Base):
    __tablename__ = "parties"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # e.g. Employer, Employee, Landlord, Tenant, Service Provider, Client
    party_type = Column(String, default="Entity")  # Individual, Corporation, LLC

    document = relationship("Document", back_populates="parties")

class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    actor = Column(String, nullable=False)  # e.g. "Employee", "Tenant"
    action = Column(String, nullable=False)  # e.g. "provide written notice"
    target_object = Column(String, nullable=True)  # e.g. "resignation notice"
    trigger = Column(String, nullable=True)  # e.g. "prior to resignation"
    deadline = Column(String, nullable=True)  # e.g. "90 days"
    duration = Column(String, nullable=True)
    condition = Column(String, nullable=True)
    is_ambiguous = Column(Boolean, default=False)
    ambiguity_reason = Column(Text, nullable=True)
    source_clause_id = Column(String, nullable=True)
    source_clause_number = Column(String, nullable=True)
    source_page = Column(Integer, default=1)
    excerpt = Column(Text, nullable=True)

    document = relationship("Document", back_populates="obligations")

class Right(Base):
    __tablename__ = "rights"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    holder = Column(String, nullable=False)  # e.g. "Employer", "Client"
    right_text = Column(String, nullable=False)  # e.g. "terminate agreement for convenience"
    condition = Column(String, nullable=True)
    source_clause_id = Column(String, nullable=True)
    source_clause_number = Column(String, nullable=True)
    source_page = Column(Integer, default=1)
    excerpt = Column(Text, nullable=True)

    document = relationship("Document", back_populates="rights")

class Deadline(Base):
    __tablename__ = "deadlines"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    event = Column(String, nullable=False)  # e.g. "Resignation notice period", "Invoice payment"
    duration_or_date = Column(String, nullable=False)  # e.g. "90 days", "30 days from invoice"
    triggering_condition = Column(String, nullable=True)
    category = Column(String, default="Notice")  # Notice, Payment, Renewal, Cure Period, Reporting
    order_index = Column(Integer, default=0)
    source_clause_id = Column(String, nullable=True)
    source_clause_number = Column(String, nullable=True)
    source_page = Column(Integer, default=1)

    document = relationship("Document", back_populates="deadlines")

class Restriction(Base):
    __tablename__ = "restrictions"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    restriction_type = Column(String, nullable=False)  # Non-compete, Non-solicit, Confidentiality, Exclusivity
    restricted_party = Column(String, nullable=False)
    activity = Column(Text, nullable=False)
    duration = Column(String, nullable=True)  # e.g. "12 months following termination"
    scope = Column(String, nullable=True)  # e.g. "Within 50 miles", "Worldwide"
    source_clause_number = Column(String, nullable=True)
    source_page = Column(Integer, default=1)

    document = relationship("Document", back_populates="restrictions")

class FinancialTerm(Base):
    __tablename__ = "financial_terms"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    item = Column(String, nullable=False)  # Base Salary, Security Deposit, Monthly Rent, Late Fee
    amount = Column(String, nullable=False)  # "$120,000", "$2,500"
    currency = Column(String, default="USD")
    frequency = Column(String, nullable=True)  # Annual, Monthly, One-off
    condition = Column(String, nullable=True)
    source_clause_number = Column(String, nullable=True)

    document = relationship("Document", back_populates="financial_terms")

class Reference(Base):
    __tablename__ = "references"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    source_clause = Column(String, nullable=False)
    target_clause = Column(String, nullable=False)
    reference_text = Column(String, nullable=True)

    document = relationship("Document", back_populates="references")

class Contradiction(Base):
    __tablename__ = "contradictions"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    title = Column(String, nullable=False)  # e.g. "Inconsistent Payment Terms"
    clause_a = Column(String, nullable=False)  # e.g. "Clause 4.1"
    text_a = Column(Text, nullable=False)
    page_a = Column(Integer, default=1)
    clause_b = Column(String, nullable=False)  # e.g. "Schedule B"
    text_b = Column(Text, nullable=False)
    page_b = Column(Integer, default=1)
    explanation = Column(Text, nullable=False)
    severity = Column(String, default="Moderate")  # Moderate, Significant

    document = relationship("Document", back_populates="contradictions")

class MissingProtection(Base):
    __tablename__ = "missing_protections"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    protection_type = Column(String, nullable=False)  # Liability Cap, Mutual Confidentiality, IP Carveout
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    severity = Column(String, default="Notice")

    document = relationship("Document", back_populates="missing_protections")

class QAMessage(Base):
    __tablename__ = "qa_messages"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=True)  # JSON list of [{document, clause, page, excerpt}]
    unsupported_claims_json = Column(Text, nullable=True)
    latency_ms = Column(Float, default=0.0)
    token_usage = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="qa_messages")

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    groundedness_score = Column(Float, default=0.0)
    citation_coverage = Column(Float, default=0.0)
    unsupported_claim_rate = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    test_cases_count = Column(Integer, default=0)
    passed_cases_count = Column(Integer, default=0)
    metrics_json = Column(Text, nullable=True)
    details_json = Column(Text, nullable=True)
