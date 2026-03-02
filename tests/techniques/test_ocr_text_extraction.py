"""Tests for OCR Text Extraction technique."""
import pytest
from parser.techniques.ocr_text_extraction import OCRTextExtraction
from parser.core.document import PDFDocument


@pytest.fixture
def ocr_extractor():
    return OCRTextExtraction()


@pytest.fixture
def sample_pdf():
    return "tests/fixtures/EFTA00009890.pdf"


def test_ocr_extractor_instantiation(ocr_extractor):
    """Test OCRTextExtraction can be instantiated."""
    assert ocr_extractor.name == "ocr_text_extraction"
    assert ocr_extractor.description


def test_ocr_extractor_can_process(ocr_extractor, sample_pdf):
    """Test OCRTextExtraction can process a text-based PDF page."""
    doc = PDFDocument(sample_pdf)
    page = doc._doc[0]
    assert ocr_extractor.can_process(page)
    doc.close()


def test_ocr_extractor_run_returns_text_boxes(ocr_extractor, sample_pdf):
    """Test OCRTextExtraction extracts text boxes with coordinates."""
    doc = PDFDocument(sample_pdf)
    page = doc._doc[0]
    result = ocr_extractor.run(page, pdf_document=doc)
    
    assert result.success
    assert result.technique_name == "ocr_text_extraction"
    assert "text_boxes" in result.data
    assert isinstance(result.data['text_boxes'], list)
    
    if result.data['text_boxes']:
        box = result.data['text_boxes'][0]
        assert 'text' in box
        assert 'x' in box
        assert 'y' in box
        assert 'width' in box
        assert 'height' in box
        assert 'confidence' in box
    
    doc.close()


def test_ocr_extractor_returns_page_dimensions(ocr_extractor, sample_pdf):
    """Test OCRTextExtraction returns page dimensions."""
    doc = PDFDocument(sample_pdf)
    page = doc._doc[0]
    result = ocr_extractor.run(page, pdf_document=doc)
    
    assert result.success
    assert "page_dimensions" in result.data
    assert "width" in result.data['page_dimensions']
    assert "height" in result.data['page_dimensions']
    
    doc.close()
