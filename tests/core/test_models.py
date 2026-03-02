"""
SQLAlchemy ORM model tests for database persistence layer.
Tests User, Document, AnalysisResult, and BatchJob models.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from parser.core.database import Base
from parser.core.models import User, Document, AnalysisResult, BatchJob


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    # Use in-memory SQLite for fast, isolated tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


class TestUserModel:
    """Test cases for User model"""
    
    def test_user_creation(self, db_session):
        """Test creating a new User"""
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_admin is False
        assert user.created_at is not None
    
    def test_user_attributes(self, db_session):
        """Test User model attributes"""
        user = User(
            username="admin_user",
            email="admin@example.com",
            hashed_password="hashed_pwd",
            is_active=True,
            is_admin=True
        )
        db_session.add(user)
        db_session.commit()
        
        retrieved = db_session.query(User).filter_by(username="admin_user").first()
        assert retrieved.is_admin is True
        assert retrieved.is_active is True
    
    def test_user_timestamps(self, db_session):
        """Test User timestamps are created"""
        user = User(
            username="time_user",
            email="time@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
    
    def test_user_repr(self, db_session):
        """Test User __repr__ method"""
        user = User(
            username="repr_user",
            email="repr@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        user_repr = repr(user)
        assert "User" in user_repr or "repr_user" in user_repr


class TestDocumentModel:
    """Test cases for Document model"""
    
    def test_document_creation(self, db_session):
        """Test creating a new Document"""
        user = User(
            username="doc_user",
            email="docuser@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="test_pdf.pdf",
            file_size=50000,
            upload_path="/uploads/test_pdf.pdf",
            page_count=10
        )
        db_session.add(doc)
        db_session.commit()
        
        assert doc.id is not None
        assert doc.filename == "test_pdf.pdf"
        assert doc.file_size == 50000
        assert doc.page_count == 10
        assert doc.status == "uploaded"
    
    def test_document_status_field(self, db_session):
        """Test Document status field"""
        user = User(
            username="status_user",
            email="status@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="status_test.pdf",
            file_size=10000,
            upload_path="/uploads/status_test.pdf",
            status="processing"
        )
        db_session.add(doc)
        db_session.commit()
        
        retrieved = db_session.query(Document).first()
        assert retrieved.status == "processing"
    
    def test_document_error_message(self, db_session):
        """Test Document error_message field"""
        user = User(
            username="error_user",
            email="error@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="error_test.pdf",
            file_size=10000,
            upload_path="/uploads/error_test.pdf",
            status="failed",
            error_message="File is corrupted"
        )
        db_session.add(doc)
        db_session.commit()
        
        retrieved = db_session.query(Document).first()
        assert retrieved.error_message == "File is corrupted"
    
    def test_document_processing_time(self, db_session):
        """Test Document processing_time field"""
        user = User(
            username="time_user",
            email="time@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="time_test.pdf",
            file_size=10000,
            upload_path="/uploads/time_test.pdf",
            processing_time=123.45
        )
        db_session.add(doc)
        db_session.commit()
        
        retrieved = db_session.query(Document).first()
        assert retrieved.processing_time == 123.45
    
    def test_document_relationship_to_user(self, db_session):
        """Test Document relationship to User"""
        user = User(
            username="rel_user",
            email="rel@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="rel_test.pdf",
            file_size=10000,
            upload_path="/uploads/rel_test.pdf"
        )
        db_session.add(doc)
        db_session.commit()
        
        assert doc.user_id == user.id
        assert doc.user.username == "rel_user"


class TestAnalysisResultModel:
    """Test cases for AnalysisResult model"""
    
    def test_analysis_result_creation(self, db_session):
        """Test creating an AnalysisResult"""
        user = User(
            username="analysis_user",
            email="analysis@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="analysis_test.pdf",
            file_size=10000,
            upload_path="/uploads/analysis_test.pdf"
        )
        db_session.add(doc)
        db_session.commit()
        
        result = AnalysisResult(
            document_id=doc.id,
            page_number=1,
            technique_name="TextLayerExtractor",
            success=True,
            confidence=0.95
        )
        db_session.add(result)
        db_session.commit()
        
        assert result.id is not None
        assert result.page_number == 1
        assert result.technique_name == "TextLayerExtractor"
        assert result.success is True
        assert result.confidence == 0.95
    
    def test_analysis_result_data_json(self, db_session):
        """Test AnalysisResult data JSON field"""
        user = User(
            username="json_user",
            email="json@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="json_test.pdf",
            file_size=10000,
            upload_path="/uploads/json_test.pdf"
        )
        db_session.add(doc)
        db_session.commit()
        
        test_data = {"text": "recovered text", "bbox": [10, 20, 100, 200]}
        result = AnalysisResult(
            document_id=doc.id,
            page_number=1,
            technique_name="EdgeAnalyzer",
            success=True,
            confidence=0.85,
            data=test_data
        )
        db_session.add(result)
        db_session.commit()
        
        retrieved = db_session.query(AnalysisResult).first()
        assert retrieved.data == test_data
        assert retrieved.data["text"] == "recovered text"
    
    def test_analysis_result_error_message(self, db_session):
        """Test AnalysisResult error_message field"""
        user = User(
            username="err_user",
            email="err@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="err_test.pdf",
            file_size=10000,
            upload_path="/uploads/err_test.pdf"
        )
        db_session.add(doc)
        db_session.commit()
        
        result = AnalysisResult(
            document_id=doc.id,
            page_number=1,
            technique_name="BarDetector",
            success=False,
            confidence=0.0,
            error_message="No bars detected"
        )
        db_session.add(result)
        db_session.commit()
        
        retrieved = db_session.query(AnalysisResult).first()
        assert retrieved.success is False
        assert retrieved.error_message == "No bars detected"
    
    def test_analysis_result_processing_time(self, db_session):
        """Test AnalysisResult processing_time field"""
        user = User(
            username="ptime_user",
            email="ptime@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="ptime_test.pdf",
            file_size=10000,
            upload_path="/uploads/ptime_test.pdf"
        )
        db_session.add(doc)
        db_session.commit()
        
        result = AnalysisResult(
            document_id=doc.id,
            page_number=1,
            technique_name="EdgeMatcher",
            success=True,
            confidence=0.90,
            processing_time=45.23
        )
        db_session.add(result)
        db_session.commit()
        
        retrieved = db_session.query(AnalysisResult).first()
        assert retrieved.processing_time == 45.23
    
    def test_analysis_result_relationship_to_document(self, db_session):
        """Test AnalysisResult relationship to Document"""
        user = User(
            username="rel_user",
            email="rel@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="rel_analysis.pdf",
            file_size=10000,
            upload_path="/uploads/rel_analysis.pdf"
        )
        db_session.add(doc)
        db_session.commit()
        
        result = AnalysisResult(
            document_id=doc.id,
            page_number=1,
            technique_name="Technique1",
            success=True,
            confidence=0.95
        )
        db_session.add(result)
        db_session.commit()
        
        assert result.document_id == doc.id
        assert result.document.filename == "rel_analysis.pdf"


class TestBatchJobModel:
    """Test cases for BatchJob model"""
    
    def test_batch_job_creation(self, db_session):
        """Test creating a BatchJob"""
        user = User(
            username="batch_user",
            email="batch@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        batch = BatchJob(
            user_id=user.id,
            batch_name="batch_001",
            status="pending",
            total_documents=5
        )
        db_session.add(batch)
        db_session.commit()
        
        assert batch.id is not None
        assert batch.batch_name == "batch_001"
        assert batch.status == "pending"
        assert batch.total_documents == 5
        assert batch.processed_documents == 0
        assert batch.failed_documents == 0
    
    def test_batch_job_attributes(self, db_session):
        """Test BatchJob attributes"""
        user = User(
            username="batch_user",
            email="batch@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        batch = BatchJob(
            user_id=user.id,
            batch_name="batch_002",
            status="processing",
            total_documents=10,
            processed_documents=3,
            failed_documents=1,
            total_time=15.5
        )
        db_session.add(batch)
        db_session.commit()
        
        retrieved = db_session.query(BatchJob).first()
        assert retrieved.processed_documents == 3
        assert retrieved.failed_documents == 1
        assert retrieved.total_time == 15.5
    
    def test_batch_job_timestamps(self, db_session):
        """Test BatchJob timestamps"""
        user = User(
            username="batch_time_user",
            email="batch_time@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        batch = BatchJob(
            user_id=user.id,
            batch_name="batch_003",
            status="completed",
            total_documents=5
        )
        db_session.add(batch)
        db_session.commit()
        
        assert batch.created_at is not None
        assert batch.started_at is None or isinstance(batch.started_at, datetime)
        assert batch.completed_at is None or isinstance(batch.completed_at, datetime)
    
    def test_batch_job_relationship_to_user(self, db_session):
        """Test BatchJob relationship to User"""
        user = User(
            username="batch_rel_user",
            email="batch_rel@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        batch = BatchJob(
            user_id=user.id,
            batch_name="batch_004",
            status="pending",
            total_documents=5
        )
        db_session.add(batch)
        db_session.commit()
        
        assert batch.user_id == user.id
        assert batch.user.username == "batch_rel_user"


class TestModelRelationships:
    """Test relationships between models"""
    
    def test_user_has_many_documents(self, db_session):
        """Test User can have multiple Documents"""
        user = User(
            username="multi_doc_user",
            email="multi@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc1 = Document(
            user_id=user.id,
            filename="doc1.pdf",
            file_size=1000,
            upload_path="/uploads/doc1.pdf"
        )
        doc2 = Document(
            user_id=user.id,
            filename="doc2.pdf",
            file_size=2000,
            upload_path="/uploads/doc2.pdf"
        )
        db_session.add_all([doc1, doc2])
        db_session.commit()
        
        retrieved_user = db_session.query(User).first()
        assert len(retrieved_user.documents) == 2
        assert retrieved_user.documents[0].filename == "doc1.pdf"
    
    def test_document_has_many_analysis_results(self, db_session):
        """Test Document can have multiple AnalysisResults"""
        user = User(
            username="multi_analysis_user",
            email="multi_analysis@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="multi_analysis.pdf",
            file_size=10000,
            upload_path="/uploads/multi_analysis.pdf"
        )
        db_session.add(doc)
        db_session.commit()
        
        result1 = AnalysisResult(
            document_id=doc.id,
            page_number=1,
            technique_name="Technique1",
            success=True,
            confidence=0.9
        )
        result2 = AnalysisResult(
            document_id=doc.id,
            page_number=1,
            technique_name="Technique2",
            success=False,
            confidence=0.5
        )
        db_session.add_all([result1, result2])
        db_session.commit()
        
        retrieved_doc = db_session.query(Document).first()
        assert len(retrieved_doc.analysis_results) == 2
        assert retrieved_doc.analysis_results[0].technique_name == "Technique1"
    
    def test_cascade_delete_document_removes_results(self, db_session):
        """Test that deleting a Document cascades to AnalysisResults"""
        user = User(
            username="cascade_user",
            email="cascade@example.com",
            hashed_password="pwd"
        )
        db_session.add(user)
        db_session.commit()
        
        doc = Document(
            user_id=user.id,
            filename="cascade_test.pdf",
            file_size=10000,
            upload_path="/uploads/cascade_test.pdf"
        )
        db_session.add(doc)
        db_session.commit()
        
        result = AnalysisResult(
            document_id=doc.id,
            page_number=1,
            technique_name="Technique1",
            success=True,
            confidence=0.9
        )
        db_session.add(result)
        db_session.commit()
        
        # Delete the document
        doc_id = doc.id
        db_session.delete(doc)
        db_session.commit()
        
        # Verify document is deleted
        deleted_doc = db_session.query(Document).filter_by(id=doc_id).first()
        assert deleted_doc is None
        
        # Verify analysis result is also deleted (cascade)
        deleted_result = db_session.query(AnalysisResult).filter_by(document_id=doc_id).first()
        assert deleted_result is None
