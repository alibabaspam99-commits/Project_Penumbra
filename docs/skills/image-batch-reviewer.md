---
name: image-batch-reviewer
description: Use when reviewing multiple extracted or generated images, need to see all at once with numbered labels for quality assessment or anomaly detection
---

# Image Batch Reviewer

## Overview

Display multiple extracted or generated images in a numbered HTML grid with gaps for efficient batch review and feedback collection. All images visible simultaneously with clear numeric identifiers for user feedback.

**Core principle:** One visual page beats multiple windows - see all candidates at once with numbered labels for easy reference.

## When to Use

**Use for:**
- Reviewing extracted features (bars, regions, anomalies)
- Quality assessment of batch processing results
- Anomaly detection and flagging (user says which numbers have issues)
- PDF validation and forensic analysis
- Generated image verification

**NOT for:**
- Single image review
- Real-time continuous streaming
- Images that need detailed manipulation

## The Technique

Create an HTML page with:
- **Flexbox grid layout** with gaps between images
- **Red numbered labels** (1, 2, 3...) above/near each image
- **Relative file paths** to local images
- **Responsive layout** that works at any browser size
- **Simple CSS** - no dependencies required

User opens the page in default browser and can review all images at once, then report feedback by number: "2, 5, and 8 have issues"

## Code Template

```html
<!DOCTYPE html>
<html>
<head>
    <title>Image Batch Review</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; padding: 20px; }
        .instructions { max-width: 1200px; margin: 0 auto 20px; 
                       background: #e3f2fd; padding: 15px; }
        .gallery { display: flex; flex-wrap: wrap; gap: 20px; 
                  justify-content: center; background: white; padding: 20px; }
        .item { display: flex; flex-direction: column; 
               align-items: center; gap: 10px; }
        .number { font-size: 24px; font-weight: bold; color: red; 
                 background: #ffffcc; padding: 5px 15px; border-radius: 5px; 
                 border: 2px solid #ff0000; }
        img { max-height: 250px; border: 1px solid #ccc; 
             border-radius: 4px; background: white; }
    </style>
</head>
<body>
    <div class="instructions">
        <h3>Batch Review - Batch N</h3>
        <p>Review images below. Tell me which numbers have issues.</p>
    </div>
    
    <div class="gallery">
        <!-- REPEAT FOR EACH IMAGE -->
        <div class="item">
            <div class="number">1</div>
            <img src="image_001.png" alt="Item 1">
        </div>
        <!-- Add more items... -->
    </div>
</body>
</html>
```

## Implementation Steps

1. **Collect image filenames** - List the N images to review
2. **Create HTML from template** - Add one `<div class="item">` block per image
3. **Update numbers** - Sequential 1, 2, 3...
4. **Update image paths** - Use relative paths (e.g., `extracted_bar_001.png`)
5. **Open in browser** - `start filename.html` (Windows) or `open filename.html` (Mac)
6. **Collect feedback** - User says which numbers have issues

## Quick Reference

| Situation | Approach |
|-----------|----------|
| Reviewing 10 extracted bars | Use template, 10 items, 250px height |
| Reviewing 50+ images | Multiple pages (batch 1-10, 11-20, etc.) |
| Showing context needed | Embed full region context in each image |
| Need image details | Add small info text below number |

## Common Mistakes

### ❌ Opening Images One-by-One
**Problem:** User flips between 10 windows, loses context, can't compare easily

**Solution:** HTML page with all visible at once

### ❌ Using PIL/OpenCV Without Installation
**Problem:** Script fails with "ModuleNotFoundError: No module named 'cv2'"

**Solution:** HTML requires zero dependencies - pure browser rendering

### ❌ Complex Image Composition Code
**Problem:** 50+ lines of image resizing, canvas creation, text rendering

**Solution:** HTML flexbox + CSS = 20 lines, instantly readable

### ❌ Hard-to-Reference Feedback
**Problem:** User says "the third one with the weird edge" - which one?

**Solution:** Numbered labels - user says "5 has an issue" - unambiguous

### ❌ No Gap Between Images
**Problem:** Images blend together, hard to distinguish boundaries

**Solution:** CSS `gap: 20px` on gallery - clear visual separation

## Workflow Example

**Scenario:** Reviewing 63 extracted redaction bars in batches of 10

```bash
# Batch 1: Create redaction_review_001.html with bars 1-10
# Open in browser, user reviews: "all good"

# Batch 2: Create redaction_review_002.html with bars 11-20
# Open in browser, user reviews: "5, 8, 12 have issues"
# Flag those three for investigation

# Continue until all reviewed
```

**Result:** Quick visual assessment, numbered feedback, traceable issues

## Real-World Impact

- **Speed:** All images visible at once (vs 10 windows)
- **Clarity:** Numbered feedback unambiguous
- **Portability:** Works in any browser, no dependencies
- **Maintenance:** Simple HTML, easy to generate programmatically
- **Repeatability:** Quick to create next batch

## Extending the Technique

**Add image metadata:**
```html
<div class="item">
    <div class="number">5</div>
    <img src="image_005.png">
    <div class="metadata">File: bar_005.png | Size: 1024x256</div>
</div>
```

**Add visual indicators:**
```html
<div class="item flagged">  <!-- CSS adds red border -->
    <div class="number">8</div>
    <img src="image_008.png">
</div>
```

**Multiple rows with section headers:**
```html
<h2>Batch 1: PDFs 1-5</h2>
<div class="gallery"><!-- images 1-10 --></div>

<h2>Batch 2: PDFs 6-10</h2>
<div class="gallery"><!-- images 11-20 --></div>
```

## Generator Script

For batch operations, use `generate-batch.py`:

```bash
# Generate batches from glob pattern
python docs/skills/generate-batch.py --pattern "extracted_bar_*.png" --batch-size 10

# Generate from specific files
python docs/skills/generate-batch.py --files "image1.png,image2.png,image3.png" --title "Review Batch 1"
```

This creates `batch_review_001.html`, `batch_review_002.html`, etc. automatically.
