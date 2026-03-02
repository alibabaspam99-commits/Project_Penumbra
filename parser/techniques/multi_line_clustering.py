"""
Multi-Line Clustering - Group vertically-adjacent bars as single redaction units.
Links bars to OCR text to classify as standard or offset multi-line patterns.
"""
from typing import List, Dict, Any, Set, Tuple
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult


class MultiLineClustering(BaseTechnique):
    """Cluster vertically-adjacent bars and link to text for classification."""
    
    name = "multi_line_clustering"
    description = "Groups adjacent bars as multi-line redactions and links to OCR text"
    
    ADJACENCY_THRESHOLD = 30  # pixels - bars closer than this are considered adjacent
    
    def can_process(self, page) -> bool:
        """Clustering doesn't depend on page, only on prior results."""
        return True
    
    def run(self, prior_results: Dict[str, Any] = None) -> TechniqueResult:
        """Cluster bars and classify as single-line or multi-line."""
        try:
            if not prior_results:
                prior_results = {}
            
            bar_results = prior_results.get('bar_detection', {})
            offset_results = prior_results.get('offset_detection', {})
            ocr_results = prior_results.get('ocr_text_extraction', {})
            
            bars = bar_results.get('bars', [])
            offset_redactions = offset_results.get('offset_redactions', [])
            text_boxes = ocr_results.get('text_boxes', [])
            
            # Find adjacent bar pairs
            adjacencies = self._find_adjacent_bars(bars)
            
            # Cluster bars using adjacency information
            clusters = self._cluster_bars(bars, adjacencies)
            
            # Link clusters to text boxes
            groups = []
            ungrouped_bars = set(range(len(bars)))
            
            for cluster in clusters:
                if len(cluster) > 1:  # Only groups of 2+ are multi-line
                    group = self._create_group(cluster, bars, offset_redactions, text_boxes)
                    groups.append(group)
                    for bar_idx in cluster:
                        ungrouped_bars.discard(bar_idx)
            
            return TechniqueResult(
                technique_name=self.name,
                success=True,
                confidence=0.90,
                data={
                    'groups': groups,
                    'ungrouped_bars': list(ungrouped_bars),
                    'multi_line_count': len([g for g in groups if g['type'] == 'multi_line']),
                    'offset_count': len([g for g in groups if g['type'] == 'multi_line_offset']),
                    'total_bars_in_groups': sum(len(g['bar_indices']) for g in groups)
                },
                error=None
            )
        
        except Exception as e:
            return TechniqueResult(
                technique_name=self.name,
                success=False,
                confidence=0.0,
                data={},
                error=f"Multi-line clustering error: {str(e)}"
            )
    
    def _find_adjacent_bars(self, bars: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
        """Find pairs of bars that are vertically adjacent."""
        adjacencies = []
        
        for i in range(len(bars)):
            for j in range(i + 1, len(bars)):
                bar_i = bars[i]
                bar_j = bars[j]
                
                # Check if bars are vertically adjacent (y ranges close)
                bar_i_y2 = bar_i.get('y2', bar_i['y'] + bar_i['h'])
                bar_j_y = bar_j['y']
                
                gap = bar_j_y - bar_i_y2
                
                if 0 < gap <= self.ADJACENCY_THRESHOLD:
                    # Also check horizontal overlap
                    bar_i_x = bar_i['x']
                    bar_i_x2 = bar_i.get('x2', bar_i['x'] + bar_i['w'])
                    bar_j_x = bar_j['x']
                    bar_j_x2 = bar_j.get('x2', bar_j['x'] + bar_j['w'])
                    
                    h_overlap = not (bar_i_x2 < bar_j_x or bar_i_x > bar_j_x2)
                    
                    if h_overlap:
                        adjacencies.append((i, j))
        
        return adjacencies
    
    def _cluster_bars(self, bars: List[Dict[str, Any]], adjacencies: List[Tuple[int, int]]) -> List[Set[int]]:
        """Use adjacency information to cluster bars into groups."""
        # Union-find style clustering
        parent = list(range(len(bars)))
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        for i, j in adjacencies:
            union(i, j)
        
        # Group bars by their root parent
        groups_dict = {}
        for i in range(len(bars)):
            root = find(i)
            if root not in groups_dict:
                groups_dict[root] = []
            groups_dict[root].append(i)
        
        return [set(group) for group in groups_dict.values()]
    
    def _create_group(self, bar_indices: Set[int], bars: List[Dict[str, Any]],
                      offset_redactions: List[Dict[str, Any]], text_boxes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a group dict from clustered bars."""
        
        # Find text boxes that overlap with these bars
        text_indices = set()
        has_gap = False
        
        for offset in offset_redactions:
            if offset['bar_idx'] in bar_indices:
                text_indices.add(offset['text_box_idx'])
                if offset['type'] == 'gap':
                    has_gap = True
        
        group_type = 'multi_line_offset' if has_gap else 'multi_line'
        
        # Calculate group composition
        total_height = 0
        bars_list = [bars[i] for i in sorted(bar_indices)]
        for bar in bars_list:
            total_height += bar.get('h', bar['y2'] - bar['y'])
        
        return {
            'type': group_type,
            'bar_indices': sorted(list(bar_indices)),
            'text_indices': sorted(list(text_indices)),
            'confidence': 0.90,
            'composition': {
                'num_bars': len(bar_indices),
                'num_text_lines': len(text_indices),
                'total_height': total_height,
                'has_gap': has_gap
            }
        }
