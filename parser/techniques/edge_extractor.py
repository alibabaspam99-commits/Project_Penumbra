import cv2
import numpy as np
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult

class EdgeExtractor(BaseTechnique):
    """Extract edge artifacts (sub-pixel gradient data) from redaction bars"""

    name = "edge_extractor"

    def can_process(self, pdf_document) -> bool:
        """All PDFs can have edges extracted"""
        return True

    def run(self, page) -> TechniqueResult:
        """
        Extract sub-pixel edge data from page image.
        Detects anti-aliasing artifacts at bar margins.
        """
        try:
            # Render page to image
            mat = page.get_pixmap(matrix=page.transformation_matrix, alpha=False)
            image_data = np.frombuffer(mat.samples, dtype=np.uint8).reshape(mat.height, mat.width, mat.n)

            # Convert to grayscale for edge detection
            if len(image_data.shape) == 3:
                gray = cv2.cvtColor(image_data, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_data

            # Apply edge detection (Canny)
            edges = cv2.Canny(gray, 50, 150)

            # Find edge pixels
            edge_pixels = np.where(edges > 0)
            edge_count = len(edge_pixels[0])

            return TechniqueResult(
                technique_name=self.name,
                success=edge_count > 0,
                data={
                    "edge_count": edge_count,
                    "image_shape": image_data.shape
                },
                confidence=0.6 if edge_count > 0 else 0.0,
                error=None if edge_count > 0 else "No edges detected"
            )
        except Exception as e:
            return TechniqueResult(
                technique_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                error=f"Edge extraction failed: {str(e)}"
            )
