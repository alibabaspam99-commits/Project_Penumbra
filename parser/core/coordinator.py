from typing import List, Dict, Optional
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult

class ParserCoordinator:
    """Orchestrates running selected techniques on PDF pages"""

    def __init__(self):
        self.techniques: Dict[str, BaseTechnique] = {}

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

    def run_phase2_page(self, page, pdf_document) -> Dict[str, TechniqueResult]:
        """
        Run Phase 2 OCR-based techniques in sequence.
        Passes prior technique results to each subsequent technique.

        Returns dict with results from all Phase 2 techniques.
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
                    results_dict['bar_detection'] = TechniqueResult(
                        technique_name='bar_detector',
                        success=False,
                        data={},
                        confidence=0.0,
                        error=f"Bar detector error: {str(e)}"
                    )

            # Step 2: Run OCR text extraction
            ocr_extractor = self.techniques.get('ocr_text_extraction')
            if ocr_extractor:
                try:
                    if ocr_extractor.can_process(page):
                        ocr_result = ocr_extractor.run(page, pdf_document=pdf_document)
                        results_dict['ocr_text_extraction'] = ocr_result
                except Exception as e:
                    results_dict['ocr_text_extraction'] = TechniqueResult(
                        technique_name='ocr_text_extraction',
                        success=False,
                        data={},
                        confidence=0.0,
                        error=f"OCR extraction error: {str(e)}"
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

                    if offset_detector.can_process(page):
                        offset_result = offset_detector.run(prior_results)
                        results_dict['offset_detection'] = offset_result
                except Exception as e:
                    results_dict['offset_detection'] = TechniqueResult(
                        technique_name='offset_detection',
                        success=False,
                        data={},
                        confidence=0.0,
                        error=f"Offset detection error: {str(e)}"
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

                    if clusterer.can_process(page):
                        clustering_result = clusterer.run(prior_results)
                        results_dict['multi_line_clustering'] = clustering_result
                except Exception as e:
                    results_dict['multi_line_clustering'] = TechniqueResult(
                        technique_name='multi_line_clustering',
                        success=False,
                        data={},
                        confidence=0.0,
                        error=f"Multi-line clustering error: {str(e)}"
                    )

            return results_dict

        except Exception as e:
            return {
                'error': f"Phase 2 processing failed: {str(e)}"
            }
