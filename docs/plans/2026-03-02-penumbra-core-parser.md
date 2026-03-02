# Project Penumbra: Core Parser Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production-ready PDF redaction parser with batch processing, interactive web visualization, and auto-alignment that enables incremental validation on small batches (3-20 images per cluster).

**Architecture:** Modular Python backend with separate technique classes orchestrated by a coordinator, streaming results via WebSocket to a React frontend. Redaction matching uses configurable alignment algorithms (top-left, center-of-mass, homography, auto-align matrix consensus) with matrix-based convergence. Incremental folder processing allows users to test with 1 PDF, add more, and re-run without reprocessing.

**Tech Stack:** Python 3.9+ (pymupdf, opencv, numpy, pillow), React/TypeScript (frontend), WebSocket (backend-frontend streaming), pytest (testing)

---

## Phase 1: Core Infrastructure & Data Models

### Task 1: Set up project structure and dependencies

**Files:**
- Create: `parser/__init__.py`
- Create: `parser/requirements.txt`
- Create: `tests/__init__.py`
- Create: `setup.py`

**Step 1: Create project scaffold**

Create `parser/__init__.py` (empty):
```python
# Parser package
```

Create `parser/requirements.txt`:
```
pymupdf==1.23.8
opencv-python==4.8.1.78
numpy==1.24.3
pillow==10.0.0
pytest==7.4.2
pytest-cov==4.1.0
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
python-multipart==0.0.6
```

Create `setup.py`:
```python
from setuptools import setup, find_packages

setup(
    name="penumbra-parser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=open("parser/requirements.txt").readlines(),
    python_requires=">=3.9",
)
```

Create `tests/__init__.py` (empty):
```python
# Tests package
```

**Step 2: Install dependencies**

Run: `cd parser && pip install -r requirements.txt`
Expected: All packages install successfully

**Step 3: Verify setup**

Run: `python -c "import pymupdf; import cv2; import numpy; print('Dependencies OK')"`
Expected: Output "Dependencies OK"

**Step 4: Commit**

```bash
git add parser/requirements.txt parser/__init__.py setup.py tests/__init__.py
git commit -m "chore: initialize project structure and dependencies"
```

---

### Task 2: Create data models for results and redactions

**Files:**
- Create: `parser/core/results.py`
- Create: `tests/core/test_results.py`

**Step 1: Write failing test**

Create `tests/core/__init__.py` (empty):
```python
```

Create `tests/core/test_results.py`:
```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/core/test_results.py -v`
Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

Create `parser/core/__init__.py`:
```python
```

Create `parser/core/results.py`:
```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/core/test_results.py -v`
Expected: PASS (4 passed)

**Step 5: Commit**

```bash
git add parser/core/__init__.py parser/core/results.py tests/core/__init__.py tests/core/test_results.py
git commit -m "feat: add core data models for results and redactions"
```

---

### Task 3: Create PDFDocument class for PDF loading and page management

**Files:**
- Create: `parser/core/document.py`
- Create: `tests/core/test_document.py`
- Create: `tests/fixtures/sample.pdf` (minimal test PDF)

**Step 1: Create minimal test PDF**

Run this Python code to create a test PDF:
```python
import fitz  # pymupdf

doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), "Sample PDF for testing")
page.insert_text((50, 100), "This is page 1")
doc.save("tests/fixtures/sample.pdf")
doc.close()
```

Run: `mkdir -p tests/fixtures && python -c "import fitz; doc = fitz.open(); page = doc.new_page(); page.insert_text((50, 50), 'Test PDF'); doc.save('tests/fixtures/sample.pdf'); doc.close()"`
Expected: File `tests/fixtures/sample.pdf` created

**Step 2: Write failing test**

Create `tests/core/test_document.py`:
```python
import pytest
from parser.core.document import PDFDocument

@pytest.fixture
def sample_pdf():
    return "tests/fixtures/sample.pdf"

def test_pdf_document_load(sample_pdf):
    """Test PDFDocument loads a PDF"""
    doc = PDFDocument(sample_pdf)
    assert doc.filename == sample_pdf
    assert doc.page_count >= 1

def test_pdf_document_get_page_count(sample_pdf):
    """Test getting page count"""
    doc = PDFDocument(sample_pdf)
    assert doc.page_count > 0

def test_pdf_document_get_page_dimensions(sample_pdf):
    """Test getting page dimensions"""
    doc = PDFDocument(sample_pdf)
    width, height = doc.get_page_dimensions(0)
    assert width > 0
    assert height > 0

def test_pdf_document_get_text_layer(sample_pdf):
    """Test extracting text layer from page"""
    doc = PDFDocument(sample_pdf)
    text = doc.get_page_text(0)
    assert isinstance(text, str)
    assert len(text) >= 0  # May be empty, that's OK
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/core/test_document.py -v`
Expected: FAIL (PDFDocument class not found)

**Step 4: Write minimal implementation**

Create `parser/core/document.py`:
```python
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
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/core/test_document.py -v`
Expected: PASS (4 passed)

**Step 6: Commit**

```bash
git add parser/core/document.py tests/core/test_document.py tests/fixtures/
git commit -m "feat: add PDFDocument class for PDF loading and page access"
```

---

### Task 4: Create BaseTechnique abstract class

**Files:**
- Create: `parser/techniques/__init__.py`
- Create: `parser/techniques/base.py`
- Create: `tests/techniques/test_base.py`

**Step 1: Write failing test**

Create `tests/techniques/__init__.py` (empty):
```python
```

Create `tests/techniques/test_base.py`:
```python
import pytest
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult

class MockTechnique(BaseTechnique):
    """Mock implementation for testing"""
    name = "mock"

    def can_process(self, pdf_document):
        return True

    def run(self, page):
        return TechniqueResult(
            technique_name=self.name,
            success=True,
            data={"test": "data"},
            confidence=0.9,
            error=None
        )

def test_base_technique_is_abstract():
    """Test BaseTechnique cannot be instantiated directly"""
    with pytest.raises(TypeError):
        BaseTechnique()

def test_mock_technique_instantiation():
    """Test concrete technique can be instantiated"""
    tech = MockTechnique()
    assert tech.name == "mock"

def test_mock_technique_run():
    """Test technique can run and return result"""
    tech = MockTechnique()
    result = tech.run(None)  # page argument not used in mock
    assert result.success is True
    assert result.confidence == 0.9
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/techniques/test_base.py -v`
Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

Create `parser/techniques/__init__.py`:
```python
```

Create `parser/techniques/base.py`:
```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/techniques/test_base.py -v`
Expected: PASS (3 passed)

**Step 5: Commit**

```bash
git add parser/techniques/__init__.py parser/techniques/base.py tests/techniques/__init__.py tests/techniques/test_base.py
git commit -m "feat: add BaseTechnique abstract class for technique framework"
```

---

### Task 5: Implement OCGLayerExtractor technique

**Files:**
- Create: `parser/techniques/ocg_layers.py`
- Create: `tests/techniques/test_ocg_layers.py`

**Step 1: Write failing test**

Create `tests/techniques/test_ocg_layers.py`:
```python
import pytest
from parser.techniques.ocg_layers import OCGLayerExtractor
from parser.core.document import PDFDocument

def test_ocg_extractor_instantiation():
    """Test OCGLayerExtractor can be created"""
    tech = OCGLayerExtractor()
    assert tech.name == "ocg_layers"

def test_ocg_extractor_can_process():
    """Test can_process returns boolean"""
    tech = OCGLayerExtractor()
    result = tech.can_process(None)
    assert isinstance(result, bool)

def test_ocg_extractor_run_returns_result():
    """Test run returns TechniqueResult"""
    tech = OCGLayerExtractor()
    result = tech.run(None)
    assert result.technique_name == "ocg_layers"
    assert isinstance(result.success, bool)
    assert isinstance(result.confidence, float)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/techniques/test_ocg_layers.py -v`
Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

Create `parser/techniques/ocg_layers.py`:
```python
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult

class OCGLayerExtractor(BaseTechnique):
    """Extract redacted text from OCG (Optional Content Group) layers in PDF"""

    name = "ocg_layers"

    def can_process(self, pdf_document) -> bool:
        """Check if PDF has OCG layers"""
        # For now, assume all PDFs could have OCG layers
        return True

    def run(self, page) -> TechniqueResult:
        """
        Attempt to extract text from OCG layers.
        Returns text if found, empty result if not present.
        """
        # Placeholder: OCG extraction would go here
        # For now, return empty result (no OCG layers found)
        return TechniqueResult(
            technique_name=self.name,
            success=False,
            data={},
            confidence=0.0,
            error="OCG extraction not yet implemented"
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/techniques/test_ocg_layers.py -v`
Expected: PASS (3 passed)

**Step 5: Commit**

```bash
git add parser/techniques/ocg_layers.py tests/techniques/test_ocg_layers.py
git commit -m "feat: add OCGLayerExtractor technique (placeholder)"
```

---

### Task 6: Implement TextLayerExtractor technique

**Files:**
- Create: `parser/techniques/text_layer.py`
- Create: `tests/techniques/test_text_layer.py`

**Step 1: Write failing test**

Create `tests/techniques/test_text_layer.py`:
```python
import pytest
from parser.techniques.text_layer import TextLayerExtractor
from parser.core.document import PDFDocument

def test_text_layer_extractor_instantiation():
    """Test TextLayerExtractor can be created"""
    tech = TextLayerExtractor()
    assert tech.name == "text_layer"

def test_text_layer_extractor_run_returns_result():
    """Test run returns TechniqueResult"""
    tech = TextLayerExtractor()
    result = tech.run(None)
    assert result.technique_name == "text_layer"
    assert isinstance(result.success, bool)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/techniques/test_text_layer.py -v`
Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

Create `parser/techniques/text_layer.py`:
```python
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult

class TextLayerExtractor(BaseTechnique):
    """Extract text directly from PDF text layer beneath redaction bars"""

    name = "text_layer"

    def can_process(self, pdf_document) -> bool:
        """All PDFs have text layers to check"""
        return True

    def run(self, page) -> TechniqueResult:
        """
        Extract text from the page's text layer.
        Some redacted text may be hidden here.
        """
        # Placeholder: text extraction would go here
        return TechniqueResult(
            technique_name=self.name,
            success=False,
            data={},
            confidence=0.0,
            error="Text layer extraction not yet implemented"
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/techniques/test_text_layer.py -v`
Expected: PASS (2 passed)

**Step 5: Commit**

```bash
git add parser/techniques/text_layer.py tests/techniques/test_text_layer.py
git commit -m "feat: add TextLayerExtractor technique (placeholder)"
```

---

### Task 7: Implement BarDetector technique

**Files:**
- Create: `parser/techniques/bar_detector.py`
- Create: `tests/techniques/test_bar_detector.py`

**Step 1: Write failing test**

Create `tests/techniques/test_bar_detector.py`:
```python
import pytest
from parser.techniques.bar_detector import BarDetector

def test_bar_detector_instantiation():
    """Test BarDetector can be created"""
    tech = BarDetector()
    assert tech.name == "bar_detector"

def test_bar_detector_run_returns_result():
    """Test run returns TechniqueResult"""
    tech = BarDetector()
    result = tech.run(None)
    assert result.technique_name == "bar_detector"
    assert isinstance(result.success, bool)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/techniques/test_bar_detector.py -v`
Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

Create `parser/techniques/bar_detector.py`:
```python
import cv2
import numpy as np
from parser.techniques.base import BaseTechnique
from parser.core.results import TechniqueResult

class BarDetector(BaseTechnique):
    """Detect black redaction bars in PDF images using OpenCV"""

    name = "bar_detector"

    def can_process(self, pdf_document) -> bool:
        """All PDFs can be searched for bars"""
        return True

    def run(self, page) -> TechniqueResult:
        """
        Detect black rectangular bars in the page image.
        Returns locations of detected bars.
        """
        # Placeholder: bar detection would go here
        return TechniqueResult(
            technique_name=self.name,
            success=False,
            data={},
            confidence=0.0,
            error="Bar detection not yet implemented"
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/techniques/test_bar_detector.py -v`
Expected: PASS (2 passed)

**Step 5: Commit**

```bash
git add parser/techniques/bar_detector.py tests/techniques/test_bar_detector.py
git commit -m "feat: add BarDetector technique (placeholder)"
```

---

### Task 8: Create ParserCoordinator to orchestrate techniques

**Files:**
- Create: `parser/core/coordinator.py`
- Create: `tests/core/test_coordinator.py`

**Step 1: Write failing test**

Create `tests/core/test_coordinator.py`:
```python
import pytest
from parser.core.coordinator import ParserCoordinator
from parser.techniques.ocg_layers import OCGLayerExtractor

def test_coordinator_instantiation():
    """Test ParserCoordinator can be created"""
    coordinator = ParserCoordinator()
    assert isinstance(coordinator.techniques, dict)

def test_coordinator_register_technique():
    """Test techniques can be registered"""
    coordinator = ParserCoordinator()
    tech = OCGLayerExtractor()
    coordinator.register_technique(tech)
    assert "ocg_layers" in coordinator.techniques

def test_coordinator_get_selected_techniques():
    """Test getting selected techniques"""
    coordinator = ParserCoordinator()
    coordinator.register_technique(OCGLayerExtractor())
    selected = coordinator.get_selected_techniques(["ocg_layers"])
    assert len(selected) == 1
    assert selected[0].name == "ocg_layers"

def test_coordinator_run_techniques():
    """Test running techniques returns results"""
    coordinator = ParserCoordinator()
    coordinator.register_technique(OCGLayerExtractor())
    results = coordinator.run_page(
        page=None,
        pdf_document=None,
        selected_techniques=["ocg_layers"]
    )
    assert len(results) == 1
    assert results[0].technique_name == "ocg_layers"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/core/test_coordinator.py -v`
Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

Create `parser/core/coordinator.py`:
```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/core/test_coordinator.py -v`
Expected: PASS (4 passed)

**Step 5: Commit**

```bash
git add parser/core/coordinator.py tests/core/test_coordinator.py
git commit -m "feat: add ParserCoordinator to orchestrate techniques"
```

---

## Phase 2: High-Priority Recovery Techniques (continued in session 2...)

---

## Execution Instructions for Parallel Session

**In a new Claude Code session:**

1. **Set working directory** to: `C:\Users\Travel\Desktop\Claude_Projects\Current_Projects\Stage_0\Project_Penumbra`

2. **Invoke the executing-plans skill**:
   ```
   /executing-plans docs/plans/2026-03-02-penumbra-core-parser.md
   ```

3. **Follow the task-by-task execution** - the skill will guide you through each task with:
   - Clear step-by-step instructions
   - Code to write/modify
   - Commands to run
   - Expected output
   - Commit guidance

4. **After each major phase**, the executing-plans skill will show you a progress checkpoint

---

**Plan document is ready.** Open a new Claude Code session pointing to this project directory and invoke the executing-plans skill to begin batch execution.