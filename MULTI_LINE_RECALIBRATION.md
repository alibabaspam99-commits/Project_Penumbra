# Multi-Line Redaction Recalibration

## What to Look For

### Single-Line Redaction (GOOD)
- **Visual**: One continuous horizontal bar
- **Pattern**: Single rectangular region, one dark bar
- **Example**: Images 1-50 (mostly)

### Multi-Line Redaction (NEEDS TAGGING)
- **Visual**: Multiple horizontal bars close together
- **Pattern**: 2+ dark regions in vertical proximity (part of same redacted section)
- **Indicator**: Several text lines all redacted together as one unit
- **Examples**: Images 51, 52, 53

### Multi-Line with Offset/Alignment Issue (SPECIAL CASE)
- **Visual**: Multiple bars with visible text offset between them
- **Pattern**: Bars don't align vertically OR text visible between bars
- **Indicator**: Redaction appears misaligned or covers partial text
- **Example**: Image 53 (text offset noted)

---

## Recalibration Process

**Review ALL batches looking for:**

1. Any image with 2+ dark bars in vertical sequence
2. Bars that appear to be redacting consecutive lines of text
3. Gaps or misalignment between bars (especially with visible text)

**Report Format:**
- **Multi-line (standard)**: "Image X - multi_line"
- **Multi-line (offset)**: "Image X - multi_line_offset_text"

---

## Suspected Images to Review

Based on visual inspection of extracted bars 1-63:
- Look for clusters of narrow bars stacked vertically
- Flag any that appear to be related (same redaction event)
- Note if they have consistent width/height across lines

---

## Phase 2 Action Items

1. **Update BarDetector**: Add clustering for vertically-adjacent bars
2. **New Category**: `multi_line` in detection results
3. **Text Analysis**: For offset cases, investigate OCR/alignment issues
4. **Re-score Accuracy**: Multi-line detection may improve overall quality

---

## Expected Pattern Changes

**Single-line only**: ~93.5% (72/77 good)
**Single + Multi-line**: Expected to find 5-10 more multi-line patterns
**Updated accuracy**: Will improve once we correctly classify all patterns
