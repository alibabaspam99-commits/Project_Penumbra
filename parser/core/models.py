"""
SQLAlchemy ORM models for the Penumbra database schema.

Models:
- User: Platform users with authentication
- Document: PDF files uploaded for analysis
- AnalysisResult: Results from individual techniques on document pages
- BatchJob: Batch processing jobs for multiple PDFs

Relationships:
- User (1) -> (N) Documents
- User (1) -> (N) BatchJobs
- Document (1) -> (N) AnalysisResults
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from parser.core.database import Base


class User(Base):
    """
    User model for platform authentication and identification.
    
    Tracks volunteers who process PDFs and their activity.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    batch_jobs = relationship("BatchJob", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_username", "username"),
        Index("idx_user_email", "email"),
        Index("idx_user_is_active", "is_active"),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Document(Base):
    """
    Document model for uploaded PDF files.
    
    Tracks metadata about PDFs including upload status,
    processing status, and analysis completion.
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(512), nullable=False)
    file_size = Column(Integer)  # in bytes
    upload_path = Column(String(1024), nullable=False)
    status = Column(String(50), default="uploaded", index=True)  # uploaded, processing, completed, failed
    page_count = Column(Integer)
    processing_time = Column(Float)  # in seconds
    error_message = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    analysis_results = relationship("AnalysisResult", back_populates="document", cascade="all, delete-orphan")
    
    # Indexes for frequent queries
    __table_args__ = (
        Index("idx_document_user_id", "user_id"),
        Index("idx_document_status", "status"),
        Index("idx_document_created_at", "created_at"),
        Index("idx_document_user_status", "user_id", "status"),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"


class AnalysisResult(Base):
    """
    AnalysisResult model for technique results.
    
    Records the output of each analysis technique on each page.
    Stores success/failure, confidence scores, and detailed data.
    """
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    technique_name = Column(String(255), nullable=False, index=True)
    success = Column(Boolean, default=False, index=True)
    confidence = Column(Float, default=0.0)  # 0.0 to 1.0
    data = Column(JSON)  # Flexible JSON storage for technique-specific data
    error_message = Column(String(512))
    processing_time = Column(Float)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    document = relationship("Document", back_populates="analysis_results")
    
    # Indexes for frequent queries
    __table_args__ = (
        Index("idx_analysis_document_id", "document_id"),
        Index("idx_analysis_technique_name", "technique_name"),
        Index("idx_analysis_page_number", "page_number"),
        Index("idx_analysis_success", "success"),
        Index("idx_analysis_doc_page", "document_id", "page_number"),
        Index("idx_analysis_doc_technique", "document_id", "technique_name"),
    )
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, technique='{self.technique_name}', success={self.success})>"


class BatchJob(Base):
    """
    BatchJob model for batch processing operations.
    
    Tracks the status of batch operations processing multiple PDFs
    at once, including progress and completion statistics.
    """
    __tablename__ = "batch_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    batch_name = Column(String(255), nullable=False)
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    total_documents = Column(Integer, default=0)
    processed_documents = Column(Integer, default=0)
    failed_documents = Column(Integer, default=0)
    total_time = Column(Float)  # in seconds, total processing time
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="batch_jobs")
    
    # Indexes for frequent queries
    __table_args__ = (
        Index("idx_batch_user_id", "user_id"),
        Index("idx_batch_status", "status"),
        Index("idx_batch_created_at", "created_at"),
        Index("idx_batch_user_status", "user_id", "status"),
    )
    
    def __repr__(self):
        return f"<BatchJob(id={self.id}, batch_name='{self.batch_name}', status='{self.status}')>"
