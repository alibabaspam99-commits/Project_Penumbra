#!/usr/bin/env python
"""
Batch Processing Demo
Demonstrates processing multiple PDFs concurrently
"""

import json
from pathlib import Path
from parser.core.coordinator import ParserCoordinator
from parser.core.batch import BatchProcessor, BatchStatus
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


def find_test_pdfs(limit=10):
    """Find test PDFs from fixtures."""
    fixture_dir = Path("tests/fixtures")
    
    if not fixture_dir.exists():
        return []
    
    # Look for individual EFTA PDFs
    pdf_files = sorted(fixture_dir.glob("EFTA*.pdf"))
    
    return pdf_files[:limit]


def progress_callback(batch_id, job):
    """Callback for batch progress updates."""
    progress = int((job.processed_count / job.total_count * 100) if job.total_count > 0 else 0)
    print(f"  [{progress:3d}%] Processed: {job.processed_count}/{job.total_count} | Failed: {job.failed_count}")


def main():
    """Run batch processing demo."""
    print("\n" + "=" * 70)
    print("PENUMBRA BATCH PROCESSING DEMO")
    print("=" * 70)
    
    # Setup
    coordinator = setup_coordinator()
    processor = BatchProcessor(coordinator, max_workers=4)
    
    print(f"\n✓ Batch processor initialized")
    print(f"✓ {len(coordinator.techniques)} techniques registered")
    print(f"✓ Max workers: 4 (concurrent processing)")
    
    # Find test PDFs
    test_pdfs = find_test_pdfs(limit=10)
    
    if not test_pdfs:
        print("\n✗ No test PDFs found in tests/fixtures/")
        return
    
    pdf_paths = [str(p) for p in test_pdfs]
    
    print(f"\n✓ Found {len(test_pdfs)} test PDFs")
    for pdf in test_pdfs[:3]:
        print(f"  - {pdf.name}")
    if len(test_pdfs) > 3:
        print(f"  ... and {len(test_pdfs) - 3} more")
    
    # Create batch job
    batch_id = "batch_demo_001"
    techniques = [
        "bar_detector",
        "image_extractor",
        "text_layer",
        "ocr_text_extraction"
    ]
    
    print(f"\n--- Creating Batch Job ---")
    print(f"Batch ID: {batch_id}")
    print(f"Techniques: {', '.join(techniques)}")
    print(f"PDFs: {len(pdf_paths)}")
    
    job = processor.create_batch(batch_id, pdf_paths, techniques)
    print(f"Status: {job.status.value}")
    
    # Process batch
    print(f"\n--- Processing Batch ---")
    print(f"Starting concurrent processing (4 workers)...\n")
    
    result = processor.process_batch(batch_id, progress_callback=progress_callback)
    
    # Summary
    print(f"\n--- Batch Summary ---")
    print(f"Status: {result['status']}")
    print(f"Processed: {result['processed']}/{result['total']}")
    print(f"Failed: {result['failed']}")
    print(f"Success Rate: {result['success_rate']}")
    print(f"Elapsed Time: {result['elapsed_seconds']:.2f}s")
    
    # Per-file results
    print(f"\n--- Per-File Results ---")
    batch_results = processor.get_batch_results(batch_id)
    
    for i, file_result in enumerate(batch_results, 1):
        status = "✓" if file_result.success else "✗"
        print(f"\n{i}. {Path(file_result.pdf_path).name}")
        print(f"   {status} Status: {'Success' if file_result.success else 'Failed'}")
        
        if file_result.success:
            print(f"   Pages analyzed: {file_result.page_count}")
            print(f"   Processing time: {file_result.processing_time:.2f}s")
            
            if file_result.technique_results:
                successes = sum(1 for r in file_result.technique_results if r['success'])
                print(f"   Techniques succeeded: {successes}/{len(file_result.technique_results)}")
        else:
            print(f"   Error: {file_result.error}")
    
    # Statistics
    print(f"\n--- Performance Statistics ---")
    total_time = result['elapsed_seconds'] or 0
    total_pdfs = len(pdf_paths)
    avg_time_per_pdf = total_time / total_pdfs if total_pdfs > 0 else 0
    
    print(f"Total PDFs processed: {total_pdfs}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per PDF: {avg_time_per_pdf:.2f}s")
    print(f"Throughput: {total_pdfs / total_time:.2f} PDFs/second" if total_time > 0 else "N/A")
    
    # Export results
    output_file = Path("batch_results.json")
    print(f"\n--- Exporting Results ---")
    if processor.export_results(batch_id, str(output_file)):
        print(f"✓ Results exported to {output_file}")
    else:
        print(f"✗ Failed to export results")
    
    # Summary for scaling
    print(f"\n--- Scaling Estimate ---")
    if avg_time_per_pdf > 0:
        time_for_100 = avg_time_per_pdf * 100
        time_for_1000 = avg_time_per_pdf * 1000
        print(f"Estimated time for 100 PDFs: {time_for_100:.1f}s ({time_for_100/60:.1f}m)")
        print(f"Estimated time for 1,000 PDFs: {time_for_1000:.1f}s ({time_for_1000/60:.1f}m)")
        print(f"With 8 workers: ~{time_for_1000/8/60:.1f}m for 1,000 PDFs")
    
    processor.cleanup()


if __name__ == "__main__":
    main()
