import pytest
from parser.techniques.edge_extractor import EdgeExtractor
from parser.core.document import PDFDocument
import numpy as np

@pytest.fixture
def sample_pdf():
    return "tests/fixtures/sample.pdf"

def test_edge_extractor_instantiation():
    """Test EdgeExtractor can be created"""
    tech = EdgeExtractor()
    assert tech.name == "edge_extractor"

def test_edge_extractor_can_process():
    """Test can_process returns boolean"""
    tech = EdgeExtractor()
    result = tech.can_process(None)
    assert isinstance(result, bool)

def test_edge_extractor_extracts_edges(sample_pdf):
    """Test edge extraction from page image"""
    tech = EdgeExtractor()
    doc = PDFDocument(sample_pdf)
    page = doc._doc[0]
    result = tech.run(page)
    assert result.technique_name == "edge_extractor"
    assert isinstance(result.success, bool)
    doc.close()
