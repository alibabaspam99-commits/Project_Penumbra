"""
Offset Detection - Identifies text positioned between or overlapping with redaction bars.

This technique compares bar positions (from bar_detection) with OCR text bounding
boxes (from ocr_text_extraction) to identify two patterns:
1. Overlap: Text that overlaps with bars (text covered by redaction)
2. Gap: Text positioned between two bars (misaligned redaction)
"""

from typing import List, Dict, Any, Tuple, Optional
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult


class OffsetDetection(BaseTechnique):
    """Detect offset patterns between redaction bars and OCR text boxes."""
    
    name = "offset_detection"
    description = "Identifies text positioned between or overlapping with redaction bars"
    
    def __init__(self):
        """Initialize the offset detector."""
        self.overlap_threshold = 0.5  # Minimum % of text box that must overlap with bar
        self.gap_vertical_tolerance = 5  # Max gap size in pixels to consider texts related
    
    def can_process(self, page) -> bool:
        """Offset detection always processes, depends on prior technique results."""
        return True
    
    def run(self, prior_results, pdf_document=None) -> TechniqueResult:
        """
        Detect offset patterns between bars and text boxes.
        
        Args:
            prior_results: Dictionary containing results from bar_detection and ocr_text_extraction
            pdf_document: Optional PDF document (for context)
        
        Returns:
            TechniqueResult with offset_redactions data
        """
        try:
            # Extract bars from prior results
            bars = []
            if prior_results and 'bar_detection' in prior_results:
                bars = prior_results['bar_detection'].get('bars', [])
            
            # Extract text boxes from prior results
            text_boxes = []
            if prior_results and 'ocr_text_extraction' in prior_results:
                text_boxes = prior_results['ocr_text_extraction'].get('text_boxes', [])
            
            # Analyze relationships between text boxes and bars
            offset_redactions = []
            flagged = []

            for text_idx, text_box in enumerate(text_boxes):
                for bar_idx, bar in enumerate(bars):
                    relationship = self._analyze_text_bar_relationship(text_box, bar)

                    if relationship and relationship['type'] in ['overlap', 'gap']:
                        score = self._calculate_alignment_score(relationship)

                        offset_item = {
                            'text_box_idx': text_idx,
                            'bar_idx': bar_idx,
                            'type': relationship['type'],
                            'gap_size': relationship.get('gap_size', 0),
                            'alignment_score': score
                        }
                        offset_redactions.append(offset_item)

                        # Flag low-confidence matches
                        if score < 0.5:
                            flagged.append({
                                'text_idx': text_idx,
                                'bar_idx': bar_idx,
                                'reason': 'low_alignment_score'
                            })

            return TechniqueResult(
                technique_name=self.name,
                success=True,
                confidence=self._calculate_overall_confidence(offset_redactions),
                data={
                    'offset_redactions': offset_redactions,
                    'flagged': flagged,
                    'offset_count': len(offset_redactions),
                    'flagged_count': len(flagged)
                },
                error=None
            )
        
        except Exception as e:
            return TechniqueResult(
                technique_name=self.name,
                success=False,
                confidence=0.0,
                data={'offset_redactions': []},
                error=f"Offset detection error: {str(e)}"
            )
    
    def _analyze_text_bar_relationship(
        self, text_box: Dict[str, Any], bar: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze relationship between a text box and a bar.
        
        Args:
            text_box: Text box with keys: x, y, width, height, text, confidence
            bar: Bar with keys: x, y, x2, y2, w, h
        
        Returns:
            Dictionary with relationship info or None if no relationship
        """
        # Extract coordinates
        text_x1 = text_box['x']
        text_y1 = text_box['y']
        text_x2 = text_x1 + text_box['width']
        text_y2 = text_y1 + text_box['height']
        
        bar_x1 = bar['x']
        bar_y1 = bar['y']
        bar_x2 = bar.get('x2', bar['x'] + bar['w'])
        bar_y2 = bar.get('y2', bar['y'] + bar['h'])
        
        # Check for vertical overlap (same general y-level)
        y_overlap = self._calculate_vertical_overlap(text_y1, text_y2, bar_y1, bar_y2)
        
        # Check for horizontal alignment (same x-range)
        x_overlap = self._calculate_horizontal_overlap(text_x1, text_x2, bar_x1, bar_x2)
        
        # Pattern 1: Overlap - text overlaps with bar
        if y_overlap > 0 and x_overlap > 0:
            # Text is covered by bar (overlapping redaction)
            overlap_area = y_overlap * x_overlap
            text_area = text_box['width'] * text_box['height']
            
            if text_area > 0:
                overlap_ratio = overlap_area / text_area
                if overlap_ratio >= self.overlap_threshold:
                    return {
                        'type': 'overlap',
                        'overlap_area': overlap_area,
                        'text_area': text_area,
                        'overlap_ratio': overlap_ratio,
                        'gap_size': 0
                    }
        
        # Pattern 2: Gap - text is between two bars or near a bar
        # Check if text is in vertical alignment with bar but separated
        if x_overlap > 0:  # Horizontally aligned with bar
            # Check vertical gap
            gap_above = bar_y1 - text_y2
            gap_below = text_y1 - bar_y2
            
            if gap_above > 0 and gap_above < 50:  # Text above bar with small gap
                return {
                    'type': 'gap',
                    'gap_size': gap_above,
                    'gap_position': 'above'
                }
            
            if gap_below > 0 and gap_below < 50:  # Text below bar with small gap
                return {
                    'type': 'gap',
                    'gap_size': gap_below,
                    'gap_position': 'below'
                }
        
        return None
    
    def _calculate_vertical_overlap(
        self, text_y1: float, text_y2: float, bar_y1: float, bar_y2: float
    ) -> float:
        """Calculate vertical overlap distance between text and bar."""
        overlap_start = max(text_y1, bar_y1)
        overlap_end = min(text_y2, bar_y2)
        
        if overlap_end <= overlap_start:
            return 0.0
        
        return overlap_end - overlap_start
    
    def _calculate_horizontal_overlap(
        self, text_x1: float, text_x2: float, bar_x1: float, bar_x2: float
    ) -> float:
        """Calculate horizontal overlap distance between text and bar."""
        overlap_start = max(text_x1, bar_x1)
        overlap_end = min(text_x2, bar_x2)
        
        if overlap_end <= overlap_start:
            return 0.0
        
        return overlap_end - overlap_start
    
    def _calculate_alignment_score(self, relationship: Dict[str, Any]) -> float:
        """
        Calculate alignment confidence score (0.0-1.0).
        
        Args:
            relationship: Relationship dictionary from _analyze_text_bar_relationship
        
        Returns:
            Float between 0.0 and 1.0
        """
        if relationship['type'] == 'overlap':
            # For overlaps, higher ratio means higher confidence
            overlap_ratio = relationship.get('overlap_ratio', 0.0)
            # Map overlap ratio to confidence (0.5-1.0 ratio -> 0.75-0.95 confidence)
            score = min(0.95, 0.5 + (overlap_ratio * 0.45))
            return score
        
        elif relationship['type'] == 'gap':
            # For gaps, smaller gap size means higher confidence
            gap_size = relationship.get('gap_size', 0)
            # Gaps of 0-5px get high confidence, 5-50px get medium confidence
            if gap_size <= 5:
                return 0.85
            elif gap_size <= 20:
                return 0.65
            else:
                return 0.45
        
        return 0.0
    
    def _calculate_overall_confidence(self, offset_redactions: List[Dict]) -> float:
        """
        Calculate overall confidence for the technique result.
        
        Args:
            offset_redactions: List of offset redaction items
        
        Returns:
            Float between 0.0 and 1.0
        """
        if not offset_redactions:
            return 0.0
        
        # Average confidence of all detections
        scores = [item['alignment_score'] for item in offset_redactions]
        return sum(scores) / len(scores) if scores else 0.0
