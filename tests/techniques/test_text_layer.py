import pytest
from parser.techniques.text_layer import TextLayerExtractor
from parser.core.document import PDFDocument

def test_text_layer_extractor_instantiation():
    """Test TextLayerExtractor can be created"""
    tech = TextLayerExtractor()
    assert tech.name == "text_layer"

def test_text_layer_extractor_run_returns_result():
    """Test run returns TechniqueResult"""
    tech = TextLayerExtractor()
    result = tech.run(None)
    assert result.technique_name == "text_layer"
    assert isinstance(result.success, bool)
