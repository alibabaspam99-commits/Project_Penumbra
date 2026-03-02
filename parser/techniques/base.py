from abc import ABC, abstractmethod
from parser.core.results import TechniqueResult

class BaseTechnique(ABC):
    """Abstract base class for all recovery techniques"""

    name: str  # Override in subclasses

    @abstractmethod
    def can_process(self, pdf_document) -> bool:
        """Check if this technique can process the document"""
        pass

    @abstractmethod
    def run(self, page) -> TechniqueResult:
        """Run the technique on a page, return result"""
        pass
