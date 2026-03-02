import pytest
from parser.techniques.ocg_layers import OCGLayerExtractor
from parser.core.document import PDFDocument

def test_ocg_extractor_instantiation():
    """Test OCGLayerExtractor can be created"""
    tech = OCGLayerExtractor()
    assert tech.name == "ocg_layers"

def test_ocg_extractor_can_process():
    """Test can_process returns boolean"""
    tech = OCGLayerExtractor()
    result = tech.can_process(None)
    assert isinstance(result, bool)

def test_ocg_extractor_run_returns_result():
    """Test run returns TechniqueResult"""
    tech = OCGLayerExtractor()
    result = tech.run(None)
    assert result.technique_name == "ocg_layers"
    assert isinstance(result.success, bool)
    assert isinstance(result.confidence, float)
