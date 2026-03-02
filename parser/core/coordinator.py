from typing import List, Dict, Optional, Any
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult

class ParserCoordinator:
    """Orchestrates running selected techniques on PDF pages"""

    def __init__(self):
        self.techniques: Dict[str, BaseTechnique] = {}

    def _create_error_result(self, technique_name: str, error_msg: str) -> TechniqueResult:
        """Create a TechniqueResult for error conditions."""
        return TechniqueResult(
            technique_name=technique_name,
            success=False,
            data={},
            confidence=0.0,
            error=error_msg
        )

    def register_technique(self, technique: BaseTechnique):
        """Register a technique for use"""
        self.techniques[technique.name] = technique

    def get_selected_techniques(self, names: List[str]) -> List[BaseTechnique]:
        """Get list of techniques by name"""
        return [self.techniques[name] for name in names if name in self.techniques]

    def run_page(
        self,
        page,
        pdf_document,
        selected_techniques: List[str]
    ) -> List[TechniqueResult]:
        """
        Run selected techniques on a page.
        Returns list of results, catching exceptions per technique.
        """
        results = []
        for technique in self.get_selected_techniques(selected_techniques):
            try:
                if technique.can_process(pdf_document):
                    result = technique.run(page)
                    results.append(result)
            except Exception as e:
                # Partial processing: log error and continue
                error_result = TechniqueResult(
                    technique_name=technique.name,
                    success=False,
                    data={},
                    confidence=0.0,
                    error=f"Exception: {str(e)}"
                )
                results.append(error_result)

        return results

    def run_phase2_page(self, page: Any, pdf_document: Any) -> Dict[str, TechniqueResult]:
        """
        Run Phase 2 OCR-based techniques in sequence with proper result passing.

        Execution order with dependencies:
        1. bar_detector(page, pdf_document) - Detects redaction bars in image
        2. ocr_text_extraction(page, pdf_document) - Extracts text and bounding boxes
        3. offset_detection(prior_results from 1-2) - Finds text-bar relationships
        4. multi_line_clustering(prior_results from 1-3) - Groups adjacent bars

        Each technique receives prior_results dict containing data from all previous techniques.

        Args:
            page: PDF page object (mupdf/fitz)
            pdf_document: PDFDocument wrapper containing document metadata

        Returns:
            Dict[str, TechniqueResult] mapping technique names to results.
            Keys: 'bar_detection', 'ocr_text_extraction', 'offset_detection', 'multi_line_clustering'

        Note:
            - Unregistered techniques are silently skipped
            - Technique-level exceptions are caught and returned as failed TechniqueResult
            - One technique failure does not prevent others from running (graceful degradation)
        """
        results_dict = {}

        try:
            # Step 1: Run bar detector (foundation technique)
            bar_detector = self.techniques.get('bar_detector')
            if bar_detector:
                try:
                    if bar_detector.can_process(page):
                        bar_result = bar_detector.run(page, pdf_document=pdf_document)
                        results_dict['bar_detection'] = bar_result
                except Exception as e:
                    results_dict['bar_detection'] = self._create_error_result(
                        'bar_detector',
                        f"Bar detector error: {str(e)}"
                    )

            # Step 2: Run OCR text extraction
            ocr_extractor = self.techniques.get('ocr_text_extraction')
            if ocr_extractor:
                try:
                    if ocr_extractor.can_process(page):
                        ocr_result = ocr_extractor.run(page, pdf_document=pdf_document)
                        results_dict['ocr_text_extraction'] = ocr_result
                except Exception as e:
                    results_dict['ocr_text_extraction'] = self._create_error_result(
                        'ocr_text_extraction',
                        f"OCR extraction error: {str(e)}"
                    )

            # Step 3: Run offset detection (depends on bar_detection and ocr_text_extraction)
            offset_detector = self.techniques.get('offset_detection')
            if offset_detector:
                try:
                    # Build prior_results dict for offset detection
                    prior_results = {}
                    if 'bar_detection' in results_dict:
                        prior_results['bar_detection'] = results_dict['bar_detection'].data
                    if 'ocr_text_extraction' in results_dict:
                        prior_results['ocr_text_extraction'] = results_dict['ocr_text_extraction'].data

                    # Offset detection depends on prior results; check returns True if results are available
                    prior_results_available = bool(prior_results)
                    if prior_results_available and offset_detector:
                        offset_result = offset_detector.run(prior_results, pdf_document=pdf_document)
                        results_dict['offset_detection'] = offset_result
                except Exception as e:
                    results_dict['offset_detection'] = self._create_error_result(
                        'offset_detection',
                        f"Offset detection error: {str(e)}"
                    )

            # Step 4: Run multi-line clustering (depends on all prior results)
            clusterer = self.techniques.get('multi_line_clustering')
            if clusterer:
                try:
                    # Build prior_results dict for clustering
                    prior_results = {}
                    if 'bar_detection' in results_dict:
                        prior_results['bar_detection'] = results_dict['bar_detection'].data
                    if 'ocr_text_extraction' in results_dict:
                        prior_results['ocr_text_extraction'] = results_dict['ocr_text_extraction'].data
                    if 'offset_detection' in results_dict:
                        prior_results['offset_detection'] = results_dict['offset_detection'].data

                    # Multi-line clustering depends on prior results; check returns True if results are available
                    prior_results_available = bool(prior_results)
                    if prior_results_available and clusterer:
                        clustering_result = clusterer.run(prior_results)
                        results_dict['multi_line_clustering'] = clustering_result
                except Exception as e:
                    results_dict['multi_line_clustering'] = self._create_error_result(
                        'multi_line_clustering',
                        f"Multi-line clustering error: {str(e)}"
                    )

            return results_dict

        except Exception as e:
            return {
                'error': TechniqueResult(
                    technique_name='phase2_coordinator',
                    success=False,
                    data={},
                    confidence=0.0,
                    error=f"Phase 2 processing failed: {str(e)}"
                )
            }
