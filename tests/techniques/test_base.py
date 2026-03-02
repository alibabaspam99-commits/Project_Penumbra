import pytest
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult

class MockTechnique(BaseTechnique):
    """Mock implementation for testing"""
    name = "mock"

    def can_process(self, pdf_document):
        return True

    def run(self, page):
        return TechniqueResult(
            technique_name=self.name,
            success=True,
            data={"test": "data"},
            confidence=0.9,
            error=None
        )

def test_base_technique_is_abstract():
    """Test BaseTechnique cannot be instantiated directly"""
    with pytest.raises(TypeError):
        BaseTechnique()

def test_mock_technique_instantiation():
    """Test concrete technique can be instantiated"""
    tech = MockTechnique()
    assert tech.name == "mock"

def test_mock_technique_run():
    """Test technique can run and return result"""
    tech = MockTechnique()
    result = tech.run(None)  # page argument not used in mock
    assert result.success is True
    assert result.confidence == 0.9
