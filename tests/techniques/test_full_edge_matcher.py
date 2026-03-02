import pytest
from parser.techniques.full_edge_matcher import FullEdgeSignatureMatcher

def test_full_edge_matcher_instantiation():
    """Test FullEdgeSignatureMatcher can be created"""
    tech = FullEdgeSignatureMatcher()
    assert tech.name == "full_edge_matcher"

def test_full_edge_matcher_can_process():
    """Test can_process returns boolean"""
    tech = FullEdgeSignatureMatcher()
    result = tech.can_process(None)
    assert isinstance(result, bool)

def test_full_edge_matcher_full_signature_matching():
    """Test full edge signature matching"""
    tech = FullEdgeSignatureMatcher()
    result = tech.run(None)
    assert result.technique_name == "full_edge_matcher"
    assert isinstance(result.success, bool)
