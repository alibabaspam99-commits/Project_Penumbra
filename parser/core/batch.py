"""
Batch processor for handling multiple PDFs efficiently.
Supports concurrent processing, progress tracking, and result aggregation.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

from parser.core.document import PDFDocument
from parser.core.coordinator import ParserCoordinator
from parser.core.results import TechniqueResult


class BatchStatus(str, Enum):
    """Batch processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class BatchJob:
    """Represents a batch processing job."""
    batch_id: str
    pdf_paths: List[str]
    techniques: List[str]
    status: BatchStatus = BatchStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    processed_count: int = 0
    failed_count: int = 0
    total_count: int = field(init=False)
    
    def __post_init__(self):
        self.total_count = len(self.pdf_paths)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "batch_id": self.batch_id,
            "status": self.status.value,
            "processed": self.processed_count,
            "failed": self.failed_count,
            "total": self.total_count,
            "progress": int((self.processed_count / self.total_count * 100) if self.total_count > 0 else 0),
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "elapsed": self.completed_at - self.started_at if self.started_at and self.completed_at else None
        }


@dataclass
class BatchResult:
    """Results from processing a single PDF in a batch."""
    pdf_path: str
    success: bool
    page_count: int = 0
    technique_results: List[Dict] = field(default_factory=list)
    error: Optional[str] = None
    processing_time: float = 0.0


class BatchProcessor:
    """
    Processes multiple PDFs in batch with concurrent execution.
    """
    
    def __init__(self, coordinator: ParserCoordinator, max_workers: int = 4):
        """
        Initialize batch processor.
        
        Args:
            coordinator: ParserCoordinator instance
            max_workers: Number of concurrent workers
        """
        self.coordinator = coordinator
        self.max_workers = max_workers
        self.jobs: Dict[str, BatchJob] = {}
        self.results: Dict[str, List[BatchResult]] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def create_batch(
        self,
        batch_id: str,
        pdf_paths: List[str],
        techniques: Optional[List[str]] = None
    ) -> BatchJob:
        """
        Create a new batch job.
        
        Args:
            batch_id: Unique batch identifier
            pdf_paths: List of PDF file paths
            techniques: List of techniques to run (default: all)
        
        Returns:
            BatchJob instance
        """
        if techniques is None:
            techniques = list(self.coordinator.techniques.keys())
        
        job = BatchJob(
            batch_id=batch_id,
            pdf_paths=pdf_paths,
            techniques=techniques
        )
        
        self.jobs[batch_id] = job
        self.results[batch_id] = []
        
        return job
    
    def get_batch(self, batch_id: str) -> Optional[BatchJob]:
        """Get batch job by ID."""
        return self.jobs.get(batch_id)
    
    def get_batch_results(self, batch_id: str) -> List[BatchResult]:
        """Get all results for a batch."""
        return self.results.get(batch_id, [])
    
    def get_batch_summary(self, batch_id: str) -> Dict:
        """
        Get summary statistics for a batch.
        
        Args:
            batch_id: Batch identifier
        
        Returns:
            Dictionary with summary stats
        """
        job = self.get_batch(batch_id)
        if not job:
            return {}
        
        results = self.get_batch_results(batch_id)
        success_count = sum(1 for r in results if r.success)
        
        summary = {
            "batch_id": batch_id,
            "status": job.status.value,
            "progress": int((job.processed_count / job.total_count * 100) if job.total_count > 0 else 0),
            "processed": job.processed_count,
            "failed": job.failed_count,
            "total": job.total_count,
            "success_rate": f"{(success_count / len(results) * 100):.1f}%" if results else "0%",
            "techniques": job.techniques,
            "elapsed_seconds": job.completed_at - job.started_at if job.started_at and job.completed_at else None
        }
        
        return summary
    
    def process_batch(
        self,
        batch_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Process all PDFs in a batch (blocking).
        
        Args:
            batch_id: Batch identifier
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Dictionary with batch results
        """
        job = self.get_batch(batch_id)
        if not job:
            return {"error": f"Batch {batch_id} not found"}
        
        job.status = BatchStatus.PROCESSING
        job.started_at = time.time()
        
        # Submit all tasks
        futures = {}
        for pdf_path in job.pdf_paths:
            future = self.executor.submit(
                self._process_single_pdf,
                pdf_path,
                job.techniques
            )
            futures[future] = pdf_path
        
        # Collect results as they complete
        for future in as_completed(futures):
            pdf_path = futures[future]
            try:
                result = future.result()
                self.results[batch_id].append(result)
                
                if result.success:
                    job.processed_count += 1
                else:
                    job.failed_count += 1
                
                # Callback for progress
                if progress_callback:
                    progress_callback(batch_id, job)
            
            except Exception as e:
                self.results[batch_id].append(
                    BatchResult(
                        pdf_path=pdf_path,
                        success=False,
                        error=str(e),
                        processing_time=0.0
                    )
                )
                job.failed_count += 1
        
        job.status = BatchStatus.COMPLETED
        job.completed_at = time.time()
        
        return self.get_batch_summary(batch_id)
    
    def _process_single_pdf(
        self,
        pdf_path: str,
        techniques: List[str]
    ) -> BatchResult:
        """
        Process a single PDF.
        
        Args:
            pdf_path: Path to PDF file
            techniques: Techniques to run
        
        Returns:
            BatchResult with processing outcome
        """
        start_time = time.time()
        
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return BatchResult(
                    pdf_path=str(pdf_path),
                    success=False,
                    error=f"File not found: {pdf_path}"
                )
            
            # Open PDF
            doc = PDFDocument(str(pdf_path))
            page_count = doc.page_count
            
            # Process each page
            all_results = []
            for page_num in range(page_count):
                page = doc._doc[page_num]
                
                # Run techniques
                page_results = self.coordinator.run_page(
                    page=page,
                    pdf_document=doc,
                    selected_techniques=techniques
                )
                
                all_results.extend(page_results)
            
            doc.close()
            
            # Format results
            technique_results = [
                {
                    "technique": r.technique_name,
                    "success": r.success,
                    "confidence": r.confidence
                }
                for r in all_results
            ]
            
            processing_time = time.time() - start_time
            
            return BatchResult(
                pdf_path=str(pdf_path),
                success=True,
                page_count=page_count,
                technique_results=technique_results,
                processing_time=processing_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return BatchResult(
                pdf_path=str(pdf_path),
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    def export_results(self, batch_id: str, output_path: str) -> bool:
        """
        Export batch results to JSON file.
        
        Args:
            batch_id: Batch identifier
            output_path: Path to save JSON file
        
        Returns:
            True if successful
        """
        try:
            job = self.get_batch(batch_id)
            results = self.get_batch_results(batch_id)
            
            if not job or not results:
                return False
            
            export_data = {
                "batch": job.to_dict(),
                "results": [asdict(r) for r in results],
                "summary": self.get_batch_summary(batch_id)
            }
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w") as f:
                json.dump(export_data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error exporting results: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up thread pool."""
        self.executor.shutdown(wait=True)
