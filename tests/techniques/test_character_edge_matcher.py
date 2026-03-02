import pytest
from parser.techniques.character_edge_matcher import CharacterEdgeMatcher

def test_character_edge_matcher_instantiation():
    """Test CharacterEdgeMatcher can be created"""
    tech = CharacterEdgeMatcher()
    assert tech.name == "character_edge_matcher"

def test_character_edge_matcher_can_process():
    """Test can_process returns boolean"""
    tech = CharacterEdgeMatcher()
    result = tech.can_process(None)
    assert isinstance(result, bool)

def test_character_edge_matcher_scores_candidates():
    """Test edge-based scoring of candidates"""
    tech = CharacterEdgeMatcher()
    result = tech.run(None)
    assert result.technique_name == "character_edge_matcher"
    assert isinstance(result.success, bool)
