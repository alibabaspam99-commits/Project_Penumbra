# Phase 2: OCR-Based Detection Strategy

## Discovery: Image 21 Multi-line Offset

**Finding**: Image 21 (original PDFs) shows multi-line offset with visible text between bars.

**Key Insight**: OCR can detect this pattern BETTER than image analysis because:
1. OCR shows actual text positioning
2. Multiple text fragments at same X position = misaligned redaction
3. Text offset = OCR coordinates don't match visual bars
4. Easier to identify which text belongs to which bar

---

## New Detection Approach

### Current (Image-Based)
- ✅ Bar detection via dark pixel clustering
- ✅ Aspect ratio filtering
- ❌ Hard to identify offset/alignment issues
- ❌ Can't distinguish between intentional spacing and misalignment

### Proposed (OCR-Complementary)
- **Extract text from page** using OCR (Tesseract or cloud API)
- **Get text bounding boxes** with coordinates
- **Detect gaps**: Text bounding boxes that fall between bars
- **Identify offset**: Text positions that don't align with bar positions
- **Flag multi-line**: Multiple text fragments with same X range but different Y

---

## Implementation Strategy for Phase 2

### Step 1: OCR Text Extraction
```python
# For each page:
text, text_boxes = ocr.extract_with_boxes(page)
# text_boxes: list of {text, x, y, width, height, confidence}
```

### Step 2: Alignment Detection
```python
for text_box in text_boxes:
    # Check if text overlaps with detected bars
    if text_overlaps_bar(text_box, bars):
        mark_as_redacted()
    elif text_near_bar(text_box, bars):
        # Text at edge = possible offset
        mark_as_offset_redaction()
```

### Step 3: Multi-Line Classification
```python
# Group overlapping text boxes
groups = cluster_overlapping_boxes(text_boxes)

for group in groups:
    if len(group) > 1:
        bar = find_corresponding_bar(group)
        if bar:
            mark_as_multi_line()
        else:
            mark_as_multi_line_offset()  # No single bar covers all
```

---

## Benefits

1. **Offset Detection**: Catches misaligned redactions (like image 21)
2. **Confidence Scoring**: OCR confidence + visual confidence = better accuracy
3. **Text Recovery Hints**: Know WHICH text is covered + offset
4. **Multi-line Classification**: Automatic grouping by text position
5. **Special Cases**: Identify partial redactions, misaligned covers

---

## Recommended OCR Libraries

### Tesseract (Free, Local)
- `pytesseract` wrapper for `tesseract-ocr`
- Returns bounding boxes (bbox)
- Good for PDFs with clear text

### Cloud OCR (Better Accuracy)
- Google Cloud Vision: Highly accurate, structured output
- Microsoft Azure: Similar accuracy, good bounding boxes
- AWS Textract: Good for documents

### Hybrid Approach
- Use Tesseract for quick detection
- Use Cloud OCR for edge cases (image 21 type)

---

## Expected Improvements

| Metric | Current | With OCR | Improvement |
|--------|---------|----------|------------|
| Single-line accuracy | 93.5% | 95%+ | +1.5% |
| Multi-line detection | 100% (3/3) | 100% (3/3) | No change |
| Offset detection | Low | 95%+ | +Huge |
| Overall accuracy | ~95% | 97%+ | +2% |

---

## Image 21 as Test Case

**Current state**: Marked as multi-line offset (visual inspection)
**With OCR**: Text boxes would show:
- Bar 1 at Y:100-120
- Text at Y:105-115 (OVERLAPPING)
- Bar 2 at Y:125-145
- Text at Y:130-140 (OVERLAPPING)
- **Gap pattern** between bars shows offset

**Action**: Image 21 becomes canonical test case for offset detection in Phase 2
