# Project Penumbra Phase 2: OCR-Based Offset & Multi-Line Detection

**Date**: 2026-03-02
**Status**: Design Approved
**Goal**: Detect multi-line redactions and offset patterns using OCR + visual bar analysis, preparing text recovery hints for Phase 3.

---

## Executive Summary

Phase 1 validated the core parser on 69 real redactions with 95% accuracy on single-line bars. Phase 2 adds OCR-based detection to identify edge cases:
- **Multi-line redactions** (images 51-53): Multiple text lines redacted as single unit
- **Offset patterns** (image 21): Text visible between bars, indicating misalignment or partial redaction

This phase focuses on detection and flagging, preparing comprehensive analysis for Phase 3 text recovery.

---

## Context & Validation Results

### Phase 1 Achievements
- ✅ Core parser framework with 10 modular techniques
- ✅ Bar detection: 93.5% accuracy (60/69 single-line bars correctly identified)
- ✅ 69 real redactions tested from original EFTA PDFs
- ✅ Pattern recognition: 3 multi-line cases, 1 special offset case identified

### Key Discoveries
1. **Batch HTML review reveals patterns** invisible in one-by-one inspection
2. **Multi-line redactions (3 cases)**: Images 51-53, standard + offset variants
3. **Image 21 canonical case**: Multi-line with text offset - OCR can detect better than visual analysis
4. **Accuracy potential**: 95% → 97%+ with OCR-based offset detection

### Why Phase 2 Matters
Current bar detection works well for single-line redactions. Multi-line and offset patterns are edge cases that require text-position analysis. OCR provides:
- Text bounding boxes with exact coordinates
- Confidence scores for each text region
- Ability to detect gaps (text between bars)
- Ability to identify alignment mismatches

---

## Design Approach

### Architecture Principles
1. **Modular techniques**: Each detection type is a separate technique in the framework
2. **Unified results**: All techniques return `TechniqueResult` for consistency
3. **Layered analysis**: Bar detection → OCR → Offset detection → Multi-line clustering
4. **Backward compatible**: Existing techniques unchanged, new ones added to pipeline

### Technology Stack
- **OCR Engine**: Tesseract (local, free, privacy-preserving)
- **Framework**: Existing ParserCoordinator (modular technique orchestration)
- **Language**: Python (consistent with Phase 1)
- **PDF Scope**: Text-based PDFs only (with extractable text layers)

---

## Components

### 1. OCR Text Extraction Technique

**Purpose**: Extract text and text bounding boxes from PDF pages using Tesseract.

**Responsibilities**:
- Load page image from PDF
- Run Tesseract OCR to get text and bounding boxes
- Convert coordinates: PDF points → page pixels
- Return text boxes with position, size, confidence

**Input**: PDF page object
**Output**: TechniqueResult with:
```python
{
    'text': "full page text",
    'text_boxes': [
        {'text': 'word', 'x': 100, 'y': 200, 'width': 50, 'height': 20, 'confidence': 0.95},
        ...
    ],
    'page_height': 1000,
    'page_width': 800
}
```

**Error Handling**:
- Tesseract not installed → return helpful error message
- Page has no text → return empty text_boxes list
- OCR fails → catch exception, return error in TechniqueResult

### 2. Offset Detection Technique

**Purpose**: Compare bar positions with OCR text positions to identify offset/gap patterns.

**Responsibilities**:
- Input bar detection results + OCR text boxes
- For each text box: check overlap with bars
- Identify text that falls between bars (gap pattern)
- Calculate alignment score (how well text aligns with bars)
- Flag low-confidence results

**Input**: Bar results + OCR results
**Output**: TechniqueResult with:
```python
{
    'offset_redactions': [
        {
            'text_box_idx': 5,
            'bar_idx': 3,
            'gap_size': 15,  # pixels between bar and text
            'alignment_score': 0.42,  # how well they align
            'type': 'offset' | 'gap' | 'overlap'
        },
        ...
    ],
    'flagged': [indices of low-confidence matches],
    'high_confidence_threshold': 0.85
}
```

**Scoring Logic**:
- Perfect alignment: text box completely overlaps bar → score 1.0
- Partial alignment: text at edge of bar → score 0.5-0.9
- Gap pattern: text between bars → score 0.2-0.5
- No alignment: isolated text → score 0.0

**Edge Cases**:
- Text overlaps multiple bars → mark all overlaps
- Text box split by bar → partial coverage handling
- Very small gaps → might be natural spacing, flag but don't reject

### 3. Multi-Line Clustering Technique

**Purpose**: Group vertically-adjacent bars as single redaction units, link to OCR text.

**Responsibilities**:
- Input bar detection + offset detection results
- Identify bars in vertical sequence (adjacent Y ranges)
- Link bars to OCR text boxes (same text group)
- Classify as multi_line (standard) or multi_line_offset (gap pattern)
- Return grouped composition

**Input**: Bar results + Offset results + OCR results
**Output**: TechniqueResult with:
```python
{
    'groups': [
        {
            'type': 'multi_line',  # or 'multi_line_offset'
            'bar_indices': [0, 1, 2],
            'text_indices': [0, 1, 2],
            'confidence': 0.92,
            'composition': {
                'num_bars': 3,
                'num_text_lines': 3,
                'total_height': 150,
                'has_gap': False
            }
        },
        ...
    ],
    'ungrouped_bars': [indices of bars not part of groups],
    'multi_line_count': 2,
    'offset_count': 1
}
```

**Grouping Algorithm**:
1. Sort bars by Y position
2. Find adjacent bars (Y gap < threshold)
3. Group consecutive bars together
4. For each group: find text boxes that overlap the group
5. Classify based on alignment scores

---

## Data Flow

```
PDF Page
  │
  ├─→ [Bar Detection] (existing)
  │   └─→ bars: [{x, y, w, h, aspect, ...}]
  │
  ├─→ [OCR Text Extraction] (new)
  │   └─→ text_boxes: [{text, x, y, w, h, confidence}]
  │
  ├─→ [Offset Detection] (new)
  │   Input: bars + text_boxes
  │   └─→ offsets: [{text_idx, bar_idx, gap, score, flag}]
  │
  └─→ [Multi-Line Clustering] (new)
      Input: bars + text_boxes + offsets
      └─→ groups: [{bars, texts, type, confidence}]

Final Output: Combined RedactionAnalysis
  - Single-line bars (standard detection)
  - Multi-line groups (clustered bars)
  - Offset patterns (flagged for Phase 3)
  - Text recovery hints (text positions, alignment info)
```

---

## Result Structure

All techniques follow the `TechniqueResult` pattern:

```python
@dataclass
class TechniqueResult:
    technique_name: str
    success: bool
    data: Dict[str, Any]
    confidence: float = 0.0
    error: Optional[str] = None
```

**OCR Technique Example**:
```python
TechniqueResult(
    technique_name="ocr_text_extraction",
    success=True,
    confidence=0.88,
    data={
        'text': "The quick brown fox...",
        'text_boxes': [...],
        'page_dimensions': {'width': 800, 'height': 1000},
        'ocr_engine': 'tesseract',
        'processing_time': 0.45
    }
)
```

---

## Error Handling & Resilience

### Per-Technique Error Handling
Each technique handles its own errors:
- OCR not installed → return error message
- Page has no text → return empty boxes (success=True, data={})
- Coordinate conversion fails → log warning, skip alignment for that box
- Bar detection returned no bars → skip offset/clustering techniques

### ParserCoordinator Resilience
- Catches exceptions from each technique
- Continues with remaining techniques if one fails
- Records failed techniques in results
- Returns partial results rather than failing entirely

### User-Facing Error Messages
- "Tesseract OCR not installed. Install: `apt-get install tesseract-ocr` (Linux) or download from [link] (Windows)"
- "Page has no extractable text. PDF might be image-only."
- "Coordinate conversion failed for page (DPI mismatch?). Check PDF metadata."

---

## Testing Strategy

### Unit Tests
- OCR extraction on sample page → verify text_boxes structure
- Coordinate conversion → verify pixel-to-point and point-to-pixel accuracy
- Offset detection logic → verify score calculation
- Multi-line grouping → verify adjacency detection and grouping logic

### Integration Tests
- Full pipeline on image 21 → verify multi_line_offset classification
- Full pipeline on images 51-53 → verify multi_line and multi_line_offset detection
- Full pipeline on images 1-50, 54-69 → verify single-line bars unaffected

### Validation on Real Data
- Run on all 69 original EFTA redactions
- Compare results to manual batch review
- Measure: detection accuracy, false positive rate, flagged uncertain cases
- Target: ≥97% overall accuracy, 0 missed multi-line patterns

### Canonical Test Cases
- **Image 21**: Multi-line offset with visible text gap
- **Images 51-52**: Standard multi-line patterns
- **Image 53**: Multi-line with text offset (similar to 21)

---

## Success Criteria

✅ **Phase 2 Complete When**:
1. All 3 new techniques implemented and tested
2. Offset detection correctly identifies image 21 pattern
3. Multi-line clustering correctly groups images 51-53
4. ParserCoordinator integrates all 4 techniques (bar + OCR + offset + clustering)
5. Accuracy improved from 95% to ≥97% on validation set
6. No regressions: single-line bar detection still 93.5%+ accurate
7. Edge cases documented and flagged for Phase 3
8. Design doc + implementation plan committed to git

---

## Phase 3 Preparation

Phase 2 output provides Phase 3 with:
- **Text positions**: Which text overlaps which bar
- **Alignment information**: How well text aligns with bars
- **Multi-line composition**: Which bars form single redaction unit
- **Confidence scores**: Which detections need verification
- **Edge cases**: Flagged uncertain matches for manual review

Phase 3 will use this information to:
- Extract text from overlapping text boxes
- Handle multi-line text recovery as single units
- Use alignment hints for font metric analysis
- Prioritize high-confidence matches first

---

## References

- Phase 1 Implementation: Core parser framework, bar detection, technique orchestration
- Validation Results: 69 redactions tested, patterns identified (ANOMALIES_TO_INVESTIGATE.md)
- OCR Strategy: Tesseract rationale, hybrid approach (PHASE2_OCR_DETECTION.md)
- Test Cases: Images 21, 51-53 documented with visual evidence

---

## Sign-Off

**Design Approved By**: User (2026-03-02)
**Ready for Implementation**: Yes
**Next Step**: Execute implementation plan using writing-plans skill
