"""
Bar Detector - Identifies redaction bars using clustering
Detects dark pixel clusters and identifies rectangular redaction bars
"""
import cv2
import numpy as np
from typing import List, Dict, Any
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult


class BarDetector(BaseTechnique):
    """Detect redaction bars using connected components clustering"""

    name = "bar_detector"
    description = "Identifies redaction bars using dark pixel clustering"

    def can_process(self, page) -> bool:
        """Check if page has image data"""
        image_list = page.get_images()
        return len(image_list) > 0

    def run(self, page, pdf_document=None) -> TechniqueResult:
        """Detect bars on page"""
        try:
            # Extract image from page
            image_list = page.get_images()
            if not image_list:
                return TechniqueResult(
                    technique_name=self.name,
                    success=False,
                    error="No images found on page"
                )

            xref = image_list[0][0]
            pix = __import__('fitz').Pixmap(pdf_document._doc, xref)

            # Convert to numpy array
            img_array = np.frombuffer(pix.samples, dtype=np.uint8)
            img = img_array.reshape((pix.height, pix.width, pix.n))

            # Handle different image formats
            if pix.n == 4:  # RGBA
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            elif pix.n == 1:  # Grayscale
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            # Detect bars
            bars = self._detect_bars_by_clustering(img)

            if not bars:
                return TechniqueResult(
                    technique_name=self.name,
                    success=False,
                    error="No bars detected"
                )

            return TechniqueResult(
                technique_name=self.name,
                success=True,
                confidence=0.95,
                data={
                    'bar_count': len(bars),
                    'bars': bars
                },
                error=None
            )

        except Exception as e:
            return TechniqueResult(
                technique_name=self.name,
                success=False,
                confidence=0.0,
                data={},
                error=f"Detection error: {str(e)}"
            )

    def _detect_bars_by_clustering(
        self, img, dark_threshold=20, min_cluster_pixels=500
    ) -> List[Dict[str, Any]]:
        """Detect redaction bars by clustering dark pixels"""
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # Find very dark pixels
        dark_mask = gray < dark_threshold

        # Connected components
        num_labels, labels = cv2.connectedComponents(dark_mask.astype(np.uint8))

        bars = []
        for label in range(1, num_labels):
            cluster_pixels = np.where(labels == label)

            if len(cluster_pixels[0]) < min_cluster_pixels:
                continue

            # Bounding box
            y_min, y_max = cluster_pixels[0].min(), cluster_pixels[0].max()
            x_min, x_max = cluster_pixels[1].min(), cluster_pixels[1].max()

            w = x_max - x_min + 1
            h = y_max - y_min + 1
            area = w * h

            # Check aspect ratio
            aspect_ratio = float(max(w, h)) / float(min(w, h)) if min(w, h) > 0 else 0

            # Accept if bar-like
            if aspect_ratio >= 1.1 and min(w, h) >= 5:
                bars.append({
                    'x': x_min,
                    'y': y_min,
                    'w': w,
                    'h': h,
                    'area': area,
                    'aspect': aspect_ratio,
                    'x2': x_max + 1,
                    'y2': y_max + 1,
                    'pixel_count': len(cluster_pixels[0])
                })

        # Sort by position
        return sorted(bars, key=lambda b: (b['y'], b['x']))
