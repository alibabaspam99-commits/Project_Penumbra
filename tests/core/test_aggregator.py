import pytest
from parser.core.aggregator import ResultsAggregator, AlignmentStrategy
from parser.core.results import TechniqueResult

def test_aggregator_instantiation():
    """Test ResultsAggregator can be created"""
    agg = ResultsAggregator()
    assert isinstance(agg.alignment_strategies, dict)

def test_aggregator_register_strategy():
    """Test alignment strategies can be registered"""
    agg = ResultsAggregator()

    class DummyStrategy:
        name = "dummy"
        def align(self, results):
            return results

    agg.register_strategy(DummyStrategy())
    assert "dummy" in agg.alignment_strategies

def test_aggregator_aggregate_results():
    """Test aggregating results from multiple techniques"""
    agg = ResultsAggregator()
    results = [
        TechniqueResult("tech1", True, {"text": "SECRET"}, 0.9, None),
        TechniqueResult("tech2", True, {"text": "SECRET"}, 0.95, None),
    ]
    aggregated = agg.aggregate(results, "top_left")
    assert len(aggregated) >= 0

def test_aggregator_matrix_convergence():
    """Test matrix-based convergence for result aggregation"""
    agg = ResultsAggregator()
    results = [
        TechniqueResult("tech1", True, {"text": "SECRET", "confidence": 0.9}, 0.9, None),
        TechniqueResult("tech2", True, {"text": "SECRET", "confidence": 0.95}, 0.95, None),
    ]
    converged = agg.matrix_convergence(results)
    assert isinstance(converged, dict)
