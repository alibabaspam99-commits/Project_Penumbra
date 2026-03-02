from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from parser.core.results import TechniqueResult
import numpy as np

class AlignmentStrategy(ABC):
    """Base class for result alignment strategies"""
    name: str

    @abstractmethod
    def align(self, results: List[TechniqueResult]) -> List[TechniqueResult]:
        """Align results according to strategy"""
        pass

class TopLeftAlignment(AlignmentStrategy):
    """Align results by top-left corner"""
    name = "top_left"

    def align(self, results: List[TechniqueResult]) -> List[TechniqueResult]:
        return results

class CenterOfMassAlignment(AlignmentStrategy):
    """Align results by center of mass"""
    name = "center_of_mass"

    def align(self, results: List[TechniqueResult]) -> List[TechniqueResult]:
        return results

class HomographyAlignment(AlignmentStrategy):
    """Align results using homography transformation"""
    name = "homography"

    def align(self, results: List[TechniqueResult]) -> List[TechniqueResult]:
        return results

class AutoAlignConsensus(AlignmentStrategy):
    """Automatically choose best alignment from consensus"""
    name = "auto_align"

    def align(self, results: List[TechniqueResult]) -> List[TechniqueResult]:
        return results

class ResultsAggregator:
    """Aggregate and align results from multiple techniques"""

    def __init__(self):
        self.alignment_strategies: Dict[str, AlignmentStrategy] = {}
        # Register default strategies
        self.register_strategy(TopLeftAlignment())
        self.register_strategy(CenterOfMassAlignment())
        self.register_strategy(HomographyAlignment())
        self.register_strategy(AutoAlignConsensus())

    def register_strategy(self, strategy: AlignmentStrategy):
        """Register an alignment strategy"""
        self.alignment_strategies[strategy.name] = strategy

    def aggregate(
        self,
        results: List[TechniqueResult],
        alignment_strategy: str = "auto_align"
    ) -> List[TechniqueResult]:
        """
        Aggregate results from multiple techniques using chosen alignment.
        Returns aligned and merged results.
        """
        if not results:
            return []

        strategy = self.alignment_strategies.get(alignment_strategy)
        if not strategy:
            strategy = self.alignment_strategies["auto_align"]

        aligned = strategy.align(results)
        return aligned

    def matrix_convergence(
        self,
        results: List[TechniqueResult]
    ) -> Dict:
        """
        Use matrix-based convergence to combine results.
        Builds confidence matrix across techniques and candidates.
        """
        if not results:
            return {}

        # Placeholder: real implementation would build confidence matrix
        # and find convergence points across techniques
        convergence_matrix = {}

        for result in results:
            if result.success:
                convergence_matrix[result.technique_name] = result.data

        return convergence_matrix
