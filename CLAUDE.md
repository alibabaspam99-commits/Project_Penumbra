# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Project Penumbra**: A distributed citizen science platform for analyzing and recovering hidden text in redacted PDFs. The project leverages multiple forensic techniques to reveal redacted content:

1. **OCG Layer Toggling** - Some PDFs have redactions as toggleable layers; reading the hidden text requires flipping a switch
2. **Text Layer Extraction** - Text remains in the underlying layer beneath visual bars and can be copy-pasted
3. **Edge Artifact Decoding** - Where text has been rasterised before the redaction bar is applied, sub-pixel gradient data (anti-aliasing artifacts) survive at bar margins and can be decoded with font metric analysis
4. **Over-redaction Analysis** - Search string attacks that solve entire clusters at once
5. **Width Filtering** - Simple arithmetic to eliminate 60-80% of non-matching candidates

The platform will be a mobile app/PWA that allows volunteers to process individual PDFs on their phones, with gamified UI and a central database for results.

## Technology Stack

- **Language**: Python (core parser), JavaScript/TypeScript (frontend)
- **Backend**: tbd
- **Frontend**: PWA (mobile-first)
- **Key Libraries** (for Python parser):
  - `pymupdf` - PDF manipulation and image extraction
  - `opencv-python` - Image processing for edge detection
  - `numpy` - Numerical operations
  - `pillow` - Image manipulation
  - `matplotlib` - Visualization and debugging

## Critical Architecture Notes

### Coordinate System (Most Common Bug Source)

PDF and image coordinates use different systems:
- **PDF text layer**: coordinates in POINTS (72 per inch), origin at BOTTOM-LEFT
- **Extracted image**: coordinates in PIXELS (at image DPI), origin at TOP-LEFT
- **Conversion formula**: `pixels = points × (DPI / 72)`
- **Y-axis flip**: `y_pixels = page_height_pixels - y_points × (DPI / 72)`

**Action**: Test coordinate conversion early with a known document.

### JPEG Artifacts Are Forensic Evidence

When extracting images via `doc.extract_image(xref)`:
- Raw JPEG bytes ARE the original JPEG (DCT coefficients are forensic evidence)
- **DO NOT** decode and re-encode; preserve original bytes separately
- Store JPEGs alongside parsed metadata for artifact analysis

### Data Processing Pipeline (Priority Order)

Process these techniques in order of effort-to-payoff ratio:

1. **OCG Layer Toggle + Text Extraction** - Seconds per file, 100% confidence, free answers
2. **Over-redaction / Search String Attack** - Text analysis only, solves entire clusters
3. **Width Filtering** - Simple arithmetic, eliminates 60-80% of candidates
4. **First/Last Character Edge Matching** - High discriminative power
5. **Full Edge Signature Matching** - Computationally expensive, resolves ambiguities
6. **Cross-Document Bayesian Aggregation** - Marginal cases become clear

## Project Roadmap

- **Phase 1** (Weeks 1-2): Proof of concept on first 1,000 files
- **Phase 2** (Weeks 3-4): Interactive demo + compelling writeup
- **Phase 3** (Weeks 4-6): PWA launch, 50,000+ files processed
- **Phase 4** (Months 2-3): Community growth, 500,000+ files, first findings
- **Phase 5** (Months 3-6): Full corpus completion, comprehensive analysis

## First Run Checklist (For Initial Parser Development)

```
□ Get 10 sample PDFs
□ Run: python parser.py sample.pdf --viz
□ Is bar_max_value > 0? (signal exists)
□ Can you see letter shapes in enhanced edge views?
□ Does the text layer contain hidden text?
□ Run: python parser.py sample.pdf --explore
□ Drag the contrast slider in interactive explorer
□ Screenshot the moment you see letter shapes
□ That screenshot is your proof of concept
```

## Key Implementation Components (When Built)

The core Python parser will include:

1. **Data Structures** - Document and redaction metadata models
2. **Core Parser Loop** - Main processing orchestration
3. **Bar Detection** - Identifying redaction bars in images
4. **Edge Data Extraction** - Capturing sub-pixel gradient data
5. **Text Layer Analysis** - Extracting hidden text from PDF text layer
6. **Font Calibration Engine** - Determining font metrics from samples
7. **Width Filtering** - Eliminating non-matching candidates
8. **Edge Matching & Scoring** - Template comparison and scoring
9. **Visualiser & Interactive Explorer** - Debug and exploration UI
10. **Cluster Analysis** - Aggregating results across documents

## Development Commands (Add as project evolves)

```bash
# Parser testing
python parser.py <pdf_path> --viz              # Visualize redactions and edge data
python parser.py <pdf_path> --explore          # Interactive contrast slider explorer

# Test first run checklist
python -m pytest tests/test_parser.py
python -m pytest tests/test_ocr_artifacts.py
python -m pytest tests/test_text_layer.py

# Backend (when implemented)
npm run dev                # Start dev server
npm run test              # Run frontend tests
npm run build             # Production build
```

## Important Context for Contributors

This project involves analyzing redacted documents in a legally and ethically sensitive area. The technical implementation is sound and the methodology has been independently validated by domain experts (99% hand-verification accuracy on small samples). The goal is automating this validated methodology.

All implementation should prioritize:
1. **Forensic accuracy** - Preserve evidence (JPEGs, coordinate systems, artifacts)
2. **Iterative improvement** - Early solves calibrate the system for better accuracy
3. **User experience** - Gamified interface to maintain contributor engagement
4. **Scalability** - Handle millions of PDFs across distributed volunteer processing

## References

- Complete specification and implementation notes are in `focus.txt`
- All technical algorithms and data flow are documented in the specification
- Hand-validation proof of concept has already been completed by domain experts
