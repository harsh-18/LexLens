from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx, txt
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, default=0)
    page_count = Column(Integer, default=1)
    
    document_type = Column(String, default="general_contract")  # employment_agreement, lease_agreement, vendor_contract, etc.
    jurisdiction = Column(String, default="Unspecified")
    language = Column(String, default="English")
    status = Column(String, default="uploaded")  # uploaded, processing, analyzed, failed
    error_message = Column(Text, nullable=True)
    
    summary = Column(Text, nullable=True)
    content_hash = Column(String, index=True, nullable=True)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pages = relationship("Page", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    clauses = relationship("Clause", back_populates="document", cascade="all, delete-orphan")
    parties = relationship("Party", back_populates="document", cascade="all, delete-orphan")
    obligations = relationship("Obligation", back_populates="document", cascade="all, delete-orphan")
    rights = relationship("Right", back_populates="document", cascade="all, delete-orphan")
    deadlines = relationship("Deadline", back_populates="document", cascade="all, delete-orphan")
    restrictions = relationship("Restriction", back_populates="document", cascade="all, delete-orphan")
    financial_terms = relationship("FinancialTerm", back_populates="document", cascade="all, delete-orphan")
    references = relationship("Reference", back_populates="document", cascade="all, delete-orphan")
    contradictions = relationship("Contradiction", back_populates="document", cascade="all, delete-orphan")
    missing_protections = relationship("MissingProtection", back_populates="document", cascade="all, delete-orphan")
    qa_messages = relationship("QAMessage", back_populates="document", cascade="all, delete-orphan")
