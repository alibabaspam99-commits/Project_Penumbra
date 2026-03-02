import pytest
from parser.core.coordinator import ParserCoordinator
from parser.techniques.ocg_layers import OCGLayerExtractor

def test_coordinator_instantiation():
    """Test ParserCoordinator can be created"""
    coordinator = ParserCoordinator()
    assert isinstance(coordinator.techniques, dict)

def test_coordinator_register_technique():
    """Test techniques can be registered"""
    coordinator = ParserCoordinator()
    tech = OCGLayerExtractor()
    coordinator.register_technique(tech)
    assert "ocg_layers" in coordinator.techniques

def test_coordinator_get_selected_techniques():
    """Test getting selected techniques"""
    coordinator = ParserCoordinator()
    coordinator.register_technique(OCGLayerExtractor())
    selected = coordinator.get_selected_techniques(["ocg_layers"])
    assert len(selected) == 1
    assert selected[0].name == "ocg_layers"

def test_coordinator_run_techniques():
    """Test running techniques returns results"""
    coordinator = ParserCoordinator()
    coordinator.register_technique(OCGLayerExtractor())
    results = coordinator.run_page(
        page=None,
        pdf_document=None,
        selected_techniques=["ocg_layers"]
    )
    assert len(results) == 1
    assert results[0].technique_name == "ocg_layers"
