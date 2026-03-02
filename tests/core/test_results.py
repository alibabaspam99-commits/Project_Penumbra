from parser.core.results import TechniqueResult, RedactionResult, PDFProcessingReport
from dataclasses import asdict

def test_technique_result_creation():
    """Test TechniqueResult can be created with success"""
    result = TechniqueResult(
        technique_name="ocg_layers",
        success=True,
        data={"text": "SECRET"},
        confidence=0.95,
        error=None
    )
    assert result.technique_name == "ocg_layers"
    assert result.success is True
    assert result.confidence == 0.95

def test_technique_result_with_error():
    """Test TechniqueResult can represent failures"""
    result = TechniqueResult(
        technique_name="bar_detector",
        success=False,
        data={},
        confidence=0.0,
        error="No bars found"
    )
    assert result.success is False
    assert result.error == "No bars found"

def test_redaction_result_creation():
    """Test RedactionResult aggregates technique results"""
    results = [
        TechniqueResult("ocg_layers", True, {"text": "SECRET"}, 1.0, None),
        TechniqueResult("bar_detector", True, {"box": (100, 200, 50, 15)}, 0.9, None),
    ]
    redaction = RedactionResult(
        page_num=1,
        location={"x": 100, "y": 200, "width": 50, "height": 15},
        technique_results=results
    )
    assert redaction.page_num == 1
    assert len(redaction.technique_results) == 2

def test_pdf_processing_report_creation():
    """Test PDFProcessingReport aggregates all redactions"""
    report = PDFProcessingReport(
        filename="test.pdf",
        pages_analyzed=5,
        redactions=[]
    )
    assert report.filename == "test.pdf"
    assert report.pages_analyzed == 5
