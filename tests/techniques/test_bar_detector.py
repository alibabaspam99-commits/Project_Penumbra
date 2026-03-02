import pytest
from parser.techniques.bar_detector import BarDetector

def test_bar_detector_instantiation():
    """Test BarDetector can be created"""
    tech = BarDetector()
    assert tech.name == "bar_detector"

def test_bar_detector_run_returns_result():
    """Test run returns TechniqueResult"""
    tech = BarDetector()
    result = tech.run(None)
    assert result.technique_name == "bar_detector"
    assert isinstance(result.success, bool)
