"""Tests for Multi-Line Clustering technique."""
import pytest
from parser.techniques.multi_line_clustering import MultiLineClustering


@pytest.fixture
def clusterer():
    return MultiLineClustering()


def test_clustering_instantiation(clusterer):
    """Test MultiLineClustering can be instantiated."""
    assert clusterer.name == "multi_line_clustering"
    assert clusterer.description


def test_clustering_can_always_process(clusterer):
    """Test clustering can always process (depends on prior techniques)."""
    assert clusterer.can_process(None) == True


def test_clustering_single_line_bars(clusterer):
    """Test clustering identifies single-line bars (no grouping)."""
    prior_results = {
        'bar_detection': {
            'bars': [
                {'x': 100, 'y': 100, 'x2': 200, 'y2': 120, 'w': 100, 'h': 20},
                {'x': 100, 'y': 200, 'x2': 200, 'y2': 220, 'w': 100, 'h': 20},
                {'x': 100, 'y': 300, 'x2': 200, 'y2': 320, 'w': 100, 'h': 20}
            ]
        },
        'ocr_text_extraction': {'text_boxes': []},
        'offset_detection': {'offset_redactions': []}
    }
    result = clusterer.run(prior_results)
    
    assert result.success
    assert len(result.data['groups']) == 0  # No adjacent bars
    assert len(result.data['ungrouped_bars']) == 3


def test_clustering_multi_line_bars(clusterer):
    """Test clustering identifies adjacent bars as multi-line."""
    prior_results = {
        'bar_detection': {
            'bars': [
                {'x': 100, 'y': 100, 'x2': 200, 'y2': 120, 'w': 100, 'h': 20},
                {'x': 100, 'y': 125, 'x2': 200, 'y2': 145, 'w': 100, 'h': 20},
                {'x': 100, 'y': 150, 'x2': 200, 'y2': 170, 'w': 100, 'h': 20}
            ]
        },
        'ocr_text_extraction': {
            'text_boxes': [
                {'text': 'line1', 'x': 100, 'y': 105, 'width': 50, 'height': 10, 'confidence': 0.95},
                {'text': 'line2', 'x': 100, 'y': 130, 'width': 50, 'height': 10, 'confidence': 0.95},
                {'text': 'line3', 'x': 100, 'y': 155, 'width': 50, 'height': 10, 'confidence': 0.95}
            ]
        },
        'offset_detection': {
            'offset_redactions': [
                {'text_box_idx': 0, 'bar_idx': 0, 'type': 'overlap', 'alignment_score': 0.95},
                {'text_box_idx': 1, 'bar_idx': 1, 'type': 'overlap', 'alignment_score': 0.95},
                {'text_box_idx': 2, 'bar_idx': 2, 'type': 'overlap', 'alignment_score': 0.95}
            ]
        }
    }
    result = clusterer.run(prior_results)

    assert result.success
    assert len(result.data['groups']) == 1  # All bars should group

    group = result.data['groups'][0]
    assert group['type'] == 'multi_line'
    assert len(group['bar_indices']) == 3
    assert len(group['text_indices']) == 3


def test_clustering_horizontal_non_overlap(clusterer):
    """Test that vertically adjacent bars without horizontal overlap don't group."""
    prior_results = {
        'bar_detection': {
            'bars': [
                {'x': 100, 'y': 100, 'x2': 200, 'y2': 120, 'w': 100, 'h': 20},
                {'x': 300, 'y': 125, 'x2': 400, 'y2': 145, 'w': 100, 'h': 20}  # No horizontal overlap
            ]
        },
        'ocr_text_extraction': {'text_boxes': []},
        'offset_detection': {'offset_redactions': []}
    }
    result = clusterer.run(prior_results)

    assert result.success
    assert len(result.data['groups']) == 0  # Should not group (no horizontal overlap)
    assert len(result.data['ungrouped_bars']) == 2


def test_clustering_partial_grouping(clusterer):
    """Test clustering with mixed grouped and ungrouped bars."""
    prior_results = {
        'bar_detection': {
            'bars': [
                {'x': 100, 'y': 100, 'x2': 200, 'y2': 120, 'w': 100, 'h': 20},
                {'x': 100, 'y': 125, 'x2': 200, 'y2': 145, 'w': 100, 'h': 20},  # Adjacent to bar 0
                {'x': 100, 'y': 200, 'x2': 200, 'y2': 220, 'w': 100, 'h': 20},   # Isolated
                {'x': 100, 'y': 225, 'x2': 200, 'y2': 245, 'w': 100, 'h': 20}    # Adjacent to bar 2
            ]
        },
        'ocr_text_extraction': {'text_boxes': []},
        'offset_detection': {'offset_redactions': []}
    }
    result = clusterer.run(prior_results)

    assert result.success
    assert len(result.data['groups']) == 2  # Two groups
    assert len(result.data['ungrouped_bars']) == 0  # All bars are grouped


def test_clustering_multi_line_offset(clusterer):
    """Test clustering identifies multi-line groups with gap patterns."""
    prior_results = {
        'bar_detection': {
            'bars': [
                {'x': 100, 'y': 100, 'x2': 200, 'y2': 120, 'w': 100, 'h': 20},
                {'x': 100, 'y': 125, 'x2': 200, 'y2': 145, 'w': 100, 'h': 20}
            ]
        },
        'ocr_text_extraction': {
            'text_boxes': [
                {'text': 'line1', 'x': 100, 'y': 105, 'width': 50, 'height': 10, 'confidence': 0.95},
                {'text': 'line2', 'x': 100, 'y': 130, 'width': 50, 'height': 10, 'confidence': 0.95}
            ]
        },
        'offset_detection': {
            'offset_redactions': [
                {'text_box_idx': 0, 'bar_idx': 0, 'type': 'overlap', 'alignment_score': 0.95},
                {'text_box_idx': 1, 'bar_idx': 1, 'type': 'gap', 'alignment_score': 0.75}  # Gap pattern
            ]
        }
    }
    result = clusterer.run(prior_results)

    assert result.success
    assert len(result.data['groups']) == 1

    group = result.data['groups'][0]
    assert group['type'] == 'multi_line_offset'  # Should be offset, not standard
    assert group['composition']['has_gap'] == True
    assert len(group['text_indices']) == 2
