import pytest
from parser.techniques.font_metrics import FontMetricsAnalyzer

def test_font_metrics_instantiation():
    """Test FontMetricsAnalyzer can be created"""
    tech = FontMetricsAnalyzer()
    assert tech.name == "font_metrics"

def test_font_metrics_can_process():
    """Test can_process returns boolean"""
    tech = FontMetricsAnalyzer()
    result = tech.can_process(None)
    assert isinstance(result, bool)

def test_font_metrics_analyzes_fonts():
    """Test font metrics analysis"""
    tech = FontMetricsAnalyzer()

    class MockPage:
        def get_text(self, format_type="dict"):
            return {"blocks": []}

    result = tech.run(MockPage())
    assert result.technique_name == "font_metrics"
    assert isinstance(result.success, bool)
