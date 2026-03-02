"""Tests for Offset Detection technique."""
import pytest
from parser.techniques.offset_detection import OffsetDetection


@pytest.fixture
def offset_detector():
    return OffsetDetection()


def test_offset_detector_instantiation(offset_detector):
    """Test OffsetDetection can be instantiated."""
    assert offset_detector.name == "offset_detection"
    assert offset_detector.description


def test_offset_detector_can_always_process(offset_detector):
    """Test OffsetDetection can always process (depends on prior techniques)."""
    assert offset_detector.can_process(None) == True


def test_offset_detection_with_no_bars(offset_detector):
    """Test OffsetDetection handles case with no bars."""
    prior_results = {}  # No bar detection results
    result = offset_detector.run(prior_results)
    
    assert result.technique_name == "offset_detection"
    # Should handle gracefully
    assert 'offset_redactions' in result.data


def test_offset_detection_with_no_text_boxes(offset_detector):
    """Test OffsetDetection handles case with no text boxes."""
    prior_results = {
        'bar_detection': {'bars': [{'x': 100, 'y': 100, 'x2': 200, 'y2': 120}]},
        'ocr_text_extraction': {'text_boxes': []}
    }
    result = offset_detector.run(prior_results)
    
    assert result.technique_name == "offset_detection"
    assert isinstance(result.data['offset_redactions'], list)


def test_offset_detection_overlapping_text_and_bar(offset_detector):
    """Test OffsetDetection identifies text overlapping with bars."""
    prior_results = {
        'bar_detection': {'bars': [{'x': 100, 'y': 100, 'x2': 200, 'y2': 120, 'w': 100, 'h': 20}]},
        'ocr_text_extraction': {
            'text_boxes': [{'text': 'secret', 'x': 110, 'y': 105, 'width': 50, 'height': 10, 'confidence': 0.95}]
        }
    }
    result = offset_detector.run(prior_results)
    
    assert result.success
    assert len(result.data['offset_redactions']) > 0
    
    offset = result.data['offset_redactions'][0]
    assert offset['text_box_idx'] == 0
    assert offset['bar_idx'] == 0
    assert offset['type'] == 'overlap'


def test_offset_detection_gap_pattern(offset_detector):
    """Test OffsetDetection identifies text between bars (gap pattern)."""
    prior_results = {
        'bar_detection': {
            'bars': [
                {'x': 100, 'y': 100, 'x2': 200, 'y2': 120, 'w': 100, 'h': 20},
                {'x': 100, 'y': 140, 'x2': 200, 'y2': 160, 'w': 100, 'h': 20}
            ]
        },
        'ocr_text_extraction': {
            'text_boxes': [
                {'text': 'text1', 'x': 110, 'y': 105, 'width': 50, 'height': 10, 'confidence': 0.95},
                {'text': 'GAP', 'x': 110, 'y': 125, 'width': 30, 'height': 10, 'confidence': 0.90},
                {'text': 'text2', 'x': 110, 'y': 145, 'width': 50, 'height': 10, 'confidence': 0.95}
            ]
        }
    }
    result = offset_detector.run(prior_results)
    
    assert result.success
    gap_items = [o for o in result.data['offset_redactions'] if o['type'] == 'gap']
    assert len(gap_items) > 0
