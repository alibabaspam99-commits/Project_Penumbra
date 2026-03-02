"""Tests for BarDetector technique"""
import pytest
from parser.techniques.bar_detector import BarDetector
from parser.core.document import PDFDocument


@pytest.fixture
def bar_detector():
    return BarDetector()


@pytest.fixture
def sample_pdf():
    return "tests/fixtures/EFTA00009890.pdf"


def test_bar_detector_instantiation(bar_detector):
    """Test BarDetector can be instantiated"""
    assert bar_detector.name == "bar_detector"
    assert bar_detector.description


def test_bar_detector_can_process(bar_detector, sample_pdf):
    """Test BarDetector can process a PDF page"""
    doc = PDFDocument(sample_pdf)
    page = doc._doc[0]
    assert bar_detector.can_process(page)
    doc.close()


def test_bar_detector_run(bar_detector, sample_pdf):
    """Test BarDetector detects bars"""
    doc = PDFDocument(sample_pdf)
    page = doc._doc[0]
    result = bar_detector.run(page, pdf_document=doc)

    assert result.success
    assert result.technique_name == "bar_detector"
    assert "bar_count" in result.data
    assert result.data['bar_count'] > 0
    doc.close()


def test_bar_detector_returns_bar_data(bar_detector, sample_pdf):
    """Test BarDetector returns proper bar data structure"""
    doc = PDFDocument(sample_pdf)
    page = doc._doc[0]
    result = bar_detector.run(page, pdf_document=doc)

    bars = result.data['bars']
    assert len(bars) > 0

    bar = bars[0]
    assert 'x' in bar
    assert 'y' in bar
    assert 'w' in bar
    assert 'h' in bar
    assert 'area' in bar
    assert 'aspect' in bar

    doc.close()
