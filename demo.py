#!/usr/bin/env python
"""
Penumbra Demo - End-to-end test of parser on real PDFs
Tests all 11 techniques on EFTA dataset
"""

import json
from pathlib import Path
from parser.core.document import PDFDocument
from parser.core.coordinator import ParserCoordinator
from parser.techniques.ocg_layers import OCGLayerExtractor
from parser.techniques.text_layer import TextLayerExtractor
from parser.techniques.bar_detector import BarDetector
from parser.techniques.image_extractor import ImageExtractor
from parser.techniques.over_redaction import OverRedactionAnalyzer
from parser.techniques.width_filter import WidthFilter
from parser.techniques.edge_extractor import EdgeExtractor
from parser.techniques.font_metrics import FontMetricsAnalyzer
from parser.techniques.character_edge_matcher import CharacterEdgeMatcher
from parser.techniques.full_edge_matcher import FullEdgeSignatureMatcher
from parser.techniques.ocr_text_extraction import OCRTextExtraction


def setup_coordinator():
    """Initialize coordinator with all techniques."""
    coordinator = ParserCoordinator()
    
    techniques = [
        OCGLayerExtractor(),
        TextLayerExtractor(),
        BarDetector(),
        ImageExtractor(),
        OverRedactionAnalyzer(),
        WidthFilter(),
        EdgeExtractor(),
        FontMetricsAnalyzer(),
        CharacterEdgeMatcher(),
        FullEdgeSignatureMatcher(),
        OCRTextExtraction(),
    ]
    
    for tech in techniques:
        coordinator.register_technique(tech)
    
    return coordinator


def analyze_pdf(pdf_path, coordinator, techniques_to_run=None):
    """
    Analyze a PDF with all techniques.
    
    Args:
        pdf_path: Path to PDF file
        coordinator: ParserCoordinator instance
        techniques_to_run: List of technique names to run (default: all)
    
    Returns:
        Dictionary with analysis results
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        return {"error": f"File not found: {pdf_path}"}
    
    print(f"\n{'='*60}")
    print(f"Analyzing: {pdf_path.name}")
    print(f"{'='*60}")
    
    try:
        # Open PDF
        doc = PDFDocument(str(pdf_path))
        print(f"✓ PDF loaded: {doc.page_count} pages")
        
        # Determine which techniques to run
        if techniques_to_run is None:
            techniques_to_run = list(coordinator.techniques.keys())
        
        # Analyze first page only for demo
        page_num = 0
        page = doc._doc[page_num]
        
        print(f"\nProcessing page {page_num + 1}...")
        print(f"Running techniques: {', '.join(techniques_to_run)}")
        print("-" * 60)
        
        # Run techniques
        results = coordinator.run_page(
            page=page,
            pdf_document=doc,
            selected_techniques=techniques_to_run
        )
        
        doc.close()
        
        # Format results
        analysis = {
            "filename": pdf_path.name,
            "page": page_num + 1,
            "total_pages": doc.page_count,
            "techniques_run": len(results),
            "results": []
        }
        
        success_count = 0
        for result in results:
            status = "✓" if result.success else "✗"
            print(f"{status} {result.technique_name:30} | confidence: {result.confidence:.2f}")
            
            if result.success:
                success_count += 1
            
            analysis["results"].append({
                "technique": result.technique_name,
                "success": result.success,
                "confidence": result.confidence,
                "error": result.error,
                "data_keys": list(result.data.keys()) if result.data else []
            })
        
        analysis["success_count"] = success_count
        analysis["success_rate"] = f"{(success_count / len(results) * 100):.1f}%"
        
        print("-" * 60)
        print(f"Summary: {success_count}/{len(results)} techniques succeeded")
        print(f"Success rate: {analysis['success_rate']}")
        
        return analysis
    
    except Exception as e:
        print(f"✗ Error analyzing PDF: {str(e)}")
        return {"error": str(e), "filename": pdf_path.name}


def find_test_pdfs(limit=5):
    """Find test PDFs from fixtures."""
    fixture_dir = Path("tests/fixtures")
    
    if not fixture_dir.exists():
        return []
    
    # Look for individual EFTA PDFs
    pdf_files = sorted(fixture_dir.glob("EFTA*.pdf"))
    
    return pdf_files[:limit]


def main():
    """Run demo analysis on test PDFs."""
    print("\n" + "=" * 60)
    print("PENUMBRA PARSER DEMO")
    print("=" * 60)
    
    # Setup
    coordinator = setup_coordinator()
    print(f"\n✓ Coordinator initialized")
    print(f"✓ {len(coordinator.techniques)} techniques registered:")
    for name in sorted(coordinator.techniques.keys()):
        print(f"  - {name}")
    
    # Find test PDFs
    test_pdfs = find_test_pdfs(limit=3)
    
    if not test_pdfs:
        print("\n✗ No test PDFs found in tests/fixtures/")
        print("  Run: python demo.py <pdf_path> to analyze a specific PDF")
        return
    
    # Analyze each PDF
    all_results = []
    for pdf_path in test_pdfs:
        result = analyze_pdf(pdf_path, coordinator)
        all_results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    
    total_success = sum(r.get("success_count", 0) for r in all_results)
    total_results = sum(len(r.get("results", [])) for r in all_results)
    
    print(f"\nFiles analyzed: {len(all_results)}")
    print(f"Total technique runs: {total_results}")
    print(f"Total successes: {total_success}")
    print(f"Overall success rate: {(total_success / total_results * 100):.1f}%")
    
    # Save results
    results_file = Path("demo_results.json")
    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n✓ Results saved to {results_file}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Analyze specific PDF provided as argument
        pdf_path = sys.argv[1]
        coordinator = setup_coordinator()
        result = analyze_pdf(pdf_path, coordinator)
        
        print("\n" + json.dumps(result, indent=2))
    else:
        # Run demo on test fixtures
        main()
