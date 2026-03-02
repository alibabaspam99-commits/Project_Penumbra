import pytest
from parser.core.document import PDFDocument

@pytest.fixture
def sample_pdf():
    return "tests/fixtures/sample.pdf"

def test_pdf_document_load(sample_pdf):
    """Test PDFDocument loads a PDF"""
    doc = PDFDocument(sample_pdf)
    assert doc.filename == sample_pdf
    assert doc.page_count >= 1

def test_pdf_document_get_page_count(sample_pdf):
    """Test getting page count"""
    doc = PDFDocument(sample_pdf)
    assert doc.page_count > 0

def test_pdf_document_get_page_dimensions(sample_pdf):
    """Test getting page dimensions"""
    doc = PDFDocument(sample_pdf)
    width, height = doc.get_page_dimensions(0)
    assert width > 0
    assert height > 0

def test_pdf_document_get_text_layer(sample_pdf):
    """Test extracting text layer from page"""
    doc = PDFDocument(sample_pdf)
    text = doc.get_page_text(0)
    assert isinstance(text, str)
    assert len(text) >= 0  # May be empty, that's OK
