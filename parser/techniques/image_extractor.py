from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult

class ImageExtractor(BaseTechnique):
    """Extract images from PDF pages for analysis"""

    name = "image_extractor"

    def can_process(self, pdf_document) -> bool:
        """All PDFs can have images extracted"""
        return True

    def run(self, page) -> TechniqueResult:
        """
        Extract images from the page.
        Returns list of image cross-references (xrefs).
        """
        try:
            # Get all images on the page
            image_list = page.get_images()
            image_xrefs = [img[0] for img in image_list]

            return TechniqueResult(
                technique_name=self.name,
                success=len(image_xrefs) > 0,
                data={"image_xrefs": image_xrefs},
                confidence=1.0 if image_xrefs else 0.0,
                error=None if image_xrefs else "No images found on page"
            )
        except Exception as e:
            return TechniqueResult(
                technique_name=self.name,
                success=False,
                data={},
                confidence=0.0,
                error=f"Image extraction failed: {str(e)}"
            )
