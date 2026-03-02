import pytest
from parser.techniques.image_extractor import ImageExtractor
from parser.core.document import PDFDocument
import os

@pytest.fixture
def sample_pdf():
    return "tests/fixtures/sample.pdf"

def test_image_extractor_instantiation():
    """Test ImageExtractor can be created"""
    tech = ImageExtractor()
    assert tech.name == "image_extractor"

def test_image_extractor_can_process():
    """Test can_process returns boolean"""
    tech = ImageExtractor()
    result = tech.can_process(None)
    assert isinstance(result, bool)

def test_image_extractor_run_returns_result(sample_pdf):
    """Test run returns TechniqueResult with image data"""
    tech = ImageExtractor()
    doc = PDFDocument(sample_pdf)
    page = doc._doc[0]
    result = tech.run(page)
    assert result.technique_name == "image_extractor"
    assert isinstance(result.success, bool)
    # If successful, should have image_xrefs in data
    if result.success:
        assert "image_xrefs" in result.data
        assert isinstance(result.data["image_xrefs"], list)
    doc.close()
