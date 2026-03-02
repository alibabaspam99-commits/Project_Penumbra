import pytest
from parser.techniques.over_redaction import OverRedactionAnalyzer

def test_over_redaction_instantiation():
    """Test OverRedactionAnalyzer can be created"""
    tech = OverRedactionAnalyzer()
    assert tech.name == "over_redaction"

def test_over_redaction_can_process():
    """Test can_process returns boolean"""
    tech = OverRedactionAnalyzer()
    result = tech.can_process(None)
    assert isinstance(result, bool)

def test_over_redaction_search_string_attack():
    """Test search string attack on text layer"""
    tech = OverRedactionAnalyzer()
    # Create a mock page object with text
    class MockPage:
        def get_text(self):
            return "This is SECRET text that should be redacted but is visible"

    result = tech.run(MockPage())
    assert result.technique_name == "over_redaction"
    assert isinstance(result.success, bool)
    # Should have candidates in data if text found
    if result.success:
        assert "candidates" in result.data
