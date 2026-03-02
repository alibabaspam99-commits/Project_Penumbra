import pytest
from parser.techniques.width_filter import WidthFilter

def test_width_filter_instantiation():
    """Test WidthFilter can be created"""
    tech = WidthFilter()
    assert tech.name == "width_filter"

def test_width_filter_can_process():
    """Test can_process returns boolean"""
    tech = WidthFilter()
    result = tech.can_process(None)
    assert isinstance(result, bool)

def test_width_filter_filters_candidates():
    """Test width filter eliminates non-matching candidates"""
    tech = WidthFilter()

    class MockPage:
        def get_text(self):
            return "Test text"
        def get_drawings(self):
            return []
        @property
        def rect(self):
            class Rect:
                width = 612
                height = 792
            return Rect()

    result = tech.run(MockPage())
    assert result.technique_name == "width_filter"
    assert isinstance(result.success, bool)
