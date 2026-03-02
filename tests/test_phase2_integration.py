"""Integration tests for Phase 2 OCR-based techniques."""
import pytest
from parser.core.coordinator import ParserCoordinator
from parser.core.document import PDFDocument
from parser.techniques.bar_detector import BarDetector
from parser.techniques.ocr_text_extraction import OCRTextExtraction
from parser.techniques.offset_detection import OffsetDetection
from parser.techniques.multi_line_clustering import MultiLineClustering


@pytest.fixture
def coordinator():
    coord = ParserCoordinator()
    coord.register_technique(BarDetector())
    coord.register_technique(OCRTextExtraction())
    coord.register_technique(OffsetDetection())
    coord.register_technique(MultiLineClustering())
    return coord


@pytest.fixture
def sample_pdf():
    return "tests/fixtures/EFTA00009890.pdf"


def test_phase2_coordinator_runs_all_techniques(coordinator, sample_pdf):
    """Test coordinator runs all Phase 2 techniques in order."""
    doc = PDFDocument(sample_pdf)
    page = doc._doc[0]
    
    results = coordinator.run_phase2_page(page, pdf_document=doc)
    
    # Should have results from all techniques
    assert 'bar_detection' in results
    assert 'ocr_text_extraction' in results
    assert 'offset_detection' in results
    assert 'multi_line_clustering' in results
    
    # All should be TechniqueResult objects
    assert hasattr(results['bar_detection'], 'technique_name')
    assert hasattr(results['offset_detection'], 'technique_name')
    
    doc.close()


def test_phase2_coordinator_passes_results_between_techniques(coordinator, sample_pdf):
    """Test coordinator passes results from one technique to next."""
    doc = PDFDocument(sample_pdf)
    page = doc._doc[0]
    
    results = coordinator.run_phase2_page(page, pdf_document=doc)
    
    # Offset detection should have access to bar and OCR results
    offset_result = results['offset_detection']
    assert offset_result.data.get('offset_redactions') is not None
    
    # Multi-line clustering should have access to all prior results
    clustering_result = results['multi_line_clustering']
    assert clustering_result.data.get('groups') is not None
    
    doc.close()
