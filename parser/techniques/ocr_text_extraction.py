"""
OCR Text Extraction - Extract text and text bounding boxes from PDF pages.
Uses Tesseract OCR to identify text regions and their coordinates.
"""
try:
    import pytesseract
except ImportError:
    pytesseract = None

import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult


class OCRTextExtraction(BaseTechnique):
    """Extract text and bounding boxes from PDF pages using Tesseract OCR."""
    
    name = "ocr_text_extraction"
    description = "Extracts text and text bounding boxes from PDF pages using Tesseract OCR"
    
    def can_process(self, page) -> bool:
        """Check if page has image data for OCR."""
        if pytesseract is None:
            return False
        image_list = page.get_images()
        return len(image_list) > 0
    
    def run(self, page, pdf_document=None) -> TechniqueResult:
        """Extract text and text boxes from page using OCR."""
        try:
            if pytesseract is None:
                return TechniqueResult(
                    technique_name=self.name,
                    success=False,
                    confidence=0.0,
                    data={},
                    error="Tesseract OCR not installed. Install: apt-get install tesseract-ocr"
                )
            
            # Extract image from page
            image_list = page.get_images()
            if not image_list:
                return TechniqueResult(
                    technique_name=self.name,
                    success=False,
                    confidence=0.0,
                    data={},
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
            
            # Convert to grayscale for OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Run Tesseract to get data
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            # Extract text boxes
            text_boxes = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text:  # Only include non-empty text
                    text_boxes.append({
                        'text': text,
                        'x': int(data['left'][i]),
                        'y': int(data['top'][i]),
                        'width': int(data['width'][i]),
                        'height': int(data['height'][i]),
                        'confidence': float(data['confidence'][i]) / 100.0
                    })
            
            return TechniqueResult(
                technique_name=self.name,
                success=True,
                confidence=np.mean([b['confidence'] for b in text_boxes]) if text_boxes else 0.0,
                data={
                    'text': ' '.join(data['text']),
                    'text_boxes': text_boxes,
                    'page_dimensions': {
                        'width': pix.width,
                        'height': pix.height
                    },
                    'ocr_engine': 'tesseract',
                    'box_count': len(text_boxes)
                },
                error=None
            )
        
        except ImportError:
            return TechniqueResult(
                technique_name=self.name,
                success=False,
                confidence=0.0,
                data={},
                error="pytesseract not installed. Install: pip install pytesseract"
            )
        except Exception as e:
            return TechniqueResult(
                technique_name=self.name,
                success=False,
                confidence=0.0,
                data={},
                error=f"OCR extraction error: {str(e)}"
            )
