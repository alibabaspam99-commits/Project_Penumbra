from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class TechniqueResult:
    """Result from a single recovery technique"""
    technique_name: str
    success: bool
    data: Dict[str, Any]
    confidence: float
    error: Optional[str] = None

@dataclass
class RedactionResult:
    """All techniques' results for a single redaction"""
    page_num: int
    location: Dict[str, float]  # {"x": float, "y": float, "width": float, "height": float}
    technique_results: List[TechniqueResult] = field(default_factory=list)

@dataclass
class PDFProcessingReport:
    """Complete report for one PDF file"""
    filename: str
    pages_analyzed: int
    redactions: List[RedactionResult] = field(default_factory=list)
    processing_errors: List[str] = field(default_factory=list)
