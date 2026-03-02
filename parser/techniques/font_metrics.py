from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult
from typing import Dict, List

class FontMetricsAnalyzer(BaseTechnique):
    """Analyze font metrics to calibrate edge matching"""

    name = "font_metrics"

    def can_process(self, pdf_document) -> bool:
        """All PDFs have font information"""
        return True

    def run(self, page) -> TechniqueResult:
        """
        Extract font metrics from page for calibration.
        Determines average character width, height, and spacing.
        """
        try:
            # Get text with font information
            text_dict = page.get_text("dict")
            blocks = text_dict.get("blocks", [])

            metrics = self._analyze_fonts(blocks)

            return TechniqueResult(
                technique_name=self.name,
                success=len(metrics) > 0,
                data={"font_metrics": metrics},
                confidence=0.8 if metrics else 0.0,
                error=None if metrics else "No fonts found"
            )
        except Exception as e:
            return TechniqueResult(
                technique_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                error=f"Font metrics analysis failed: {str(e)}"
            )

    def _analyze_fonts(self, blocks: List) -> Dict:
        """Extract font metrics from text blocks"""
        font_metrics = {}
        char_widths = []
        char_heights = []
        font_names = set()
        font_sizes = []
        
        for block in blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        # Extract font information
                        font_name = span.get("font", "unknown")
                        font_size = span.get("size", 0)
                        bbox = span.get("bbox", [0, 0, 0, 0])
                        
                        if font_name:
                            font_names.add(font_name)
                        if font_size > 0:
                            font_sizes.append(font_size)
                        
                        # Estimate character dimensions
                        text = span.get("text", "")
                        if text and len(text) > 0:
                            x0, y0, x1, y1 = bbox
                            width = x1 - x0
                            height = y1 - y0
                            
                            if width > 0 and height > 0:
                                avg_char_width = width / len(text)
                                char_widths.append(avg_char_width)\n                                char_heights.append(height)
        
        # Calculate aggregate metrics
        if char_widths and char_heights and font_sizes:
            font_metrics = {
                "avg_char_width": sum(char_widths) / len(char_widths),
                "min_char_width": min(char_widths),
                "max_char_width": max(char_widths),
                "avg_char_height": sum(char_heights) / len(char_heights),
                "min_char_height": min(char_heights),
                "max_char_height": max(char_heights),
                "avg_font_size": sum(font_sizes) / len(font_sizes),
                "fonts_detected": list(font_names),
                "samples_analyzed": len(char_widths)
            }
        
        return font_metrics
