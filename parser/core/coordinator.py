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
