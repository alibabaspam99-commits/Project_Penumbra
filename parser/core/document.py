import fitz
from typing import Tuple

class PDFDocument:
    """Wrapper for PyMuPDF document with utility methods"""

    def __init__(self, filename: str):
        self.filename = filename
        self._doc = fitz.open(filename)

    @property
    def page_count(self) -> int:
        """Get total number of pages"""
        return self._doc.page_count

    def get_page_dimensions(self, page_num: int) -> Tuple[float, float]:
        """Get width, height of a page in pixels at 72 DPI"""
        page = self._doc[page_num]
        rect = page.rect
        return rect.width, rect.height

    def get_page_text(self, page_num: int) -> str:
        """Extract text layer from page"""
        page = self._doc[page_num]
        return page.get_text()

    def close(self):
        """Close the document"""
        self._doc.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
