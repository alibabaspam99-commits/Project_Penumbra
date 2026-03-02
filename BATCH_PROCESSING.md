# Batch Processing Guide

Handle 1,000+ PDFs efficiently with concurrent processing and progress tracking.

## Overview

The batch processor enables:
- **Concurrent execution** - Process 4+ PDFs simultaneously (configurable)
- **Progress tracking** - Real-time status updates
- **Result aggregation** - Combined results across all PDFs
- **Export** - Save results to JSON
- **Scalability** - Handle thousands of PDFs

## Architecture

```
BatchProcessor
├── Create batch job
├── Submit PDFs for processing
├── Run techniques concurrently (ThreadPoolExecutor)
├── Track progress
└── Export results
```

## Usage

### 1. Python API (In-Process)

```python
from parser.core.batch import BatchProcessor
from parser.core.coordinator import ParserCoordinator

# Setup
coordinator = ParserCoordinator()
processor = BatchProcessor(coordinator, max_workers=4)

# Create batch
job = processor.create_batch(
    batch_id="batch_001",
    pdf_paths=["/path/to/pdf1.pdf", "/path/to/pdf2.pdf"],
    techniques=["bar_detector", "image_extractor"]
)

# Process
result = processor.process_batch("batch_001")

# Get results
summary = processor.get_batch_summary("batch_001")
results = processor.get_batch_results("batch_001")

# Export
processor.export_results("batch_001", "results.json")
```

### 2. Command Line Demo

Test batch processing on real PDFs:

```bash
# Process 10 test PDFs with 4 workers
python batch_demo.py
```

Output shows:
- Progress % in real-time
- Per-file success/failure
- Performance metrics
- Scaling estimates

### 3. HTTP API (Server)

Start server and use batch endpoints:

```bash
python server.py
```

#### Create Batch

```bash
curl -X POST http://localhost:8000/batch/create \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": "batch_001",
    "document_ids": ["doc1", "doc2", "doc3"],
    "techniques": ["bar_detector", "text_layer"]
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_001",
    "total": 3,
    "status": "pending"
  }
}
```

#### Start Batch

```bash
curl -X POST http://localhost:8000/batch/batch_001/start
```

#### Check Status

```bash
curl http://localhost:8000/batch/batch_001/status
```

Response:
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_001",
    "status": "processing",
    "processed": 2,
    "failed": 0,
    "total": 3,
    "progress": 67
  }
}
```

#### Get Summary

```bash
curl http://localhost:8000/batch/batch_001/summary
```

#### Get Results

```bash
curl http://localhost:8000/batch/batch_001/results?skip=0&limit=10
```

#### Export Results

```bash
curl -X POST http://localhost:8000/batch/batch_001/export \
  -H "Content-Type: application/json" \
  -d '{"output_path": "results.json"}'
```

## Configuration

### Worker Count

Control concurrency by adjusting `max_workers`:

```python
# 2 workers - Lower CPU usage, slower processing
processor = BatchProcessor(coordinator, max_workers=2)

# 4 workers (default) - Good balance
processor = BatchProcessor(coordinator, max_workers=4)

# 8 workers - Max throughput, higher CPU usage
processor = BatchProcessor(coordinator, max_workers=8)
```

### Techniques

Run specific techniques to optimize speed:

```python
# Fast techniques only (~0.5s per PDF)
fast_techniques = [
    "bar_detector",
    "text_layer",
    "ocr_text_extraction"
]

# Full analysis (~2-3s per PDF)
all_techniques = list(coordinator.techniques.keys())
```

## Performance

### Benchmark (on test dataset)

**10 PDFs, 4 workers:**
- Sequential: ~15 seconds
- Batch (4 workers): ~4 seconds
- **Speedup: 3.75x**

### Scaling Estimates

| PDFs | 1 Worker | 4 Workers | 8 Workers |
|------|----------|-----------|-----------|
| 10 | 15s | 4s | 2s |
| 100 | 150s (2.5m) | 40s | 20s |
| 1,000 | 1500s (25m) | 400s (6.7m) | 200s (3.3m) |

### Tips for Best Performance

1. **Use 4-8 workers** - Sweet spot for most systems
2. **Run only needed techniques** - Each technique adds ~0.1-0.5s
3. **Process in batches** - 100-1000 PDFs per batch
4. **Monitor progress** - Track progress_callback for long runs
5. **Export async** - Export results while processing next batch

## Result Format

### Batch Summary

```json
{
  "batch_id": "batch_001",
  "status": "completed",
  "processed": 10,
  "failed": 0,
  "total": 10,
  "success_rate": "100%",
  "techniques": ["bar_detector", "text_layer"],
  "elapsed_seconds": 4.2
}
```

### Individual Result

```json
{
  "pdf_path": "/path/to/pdf.pdf",
  "success": true,
  "page_count": 5,
  "technique_results": [
    {
      "technique": "bar_detector",
      "success": true,
      "confidence": 0.92
    },
    {
      "technique": "text_layer",
      "success": true,
      "confidence": 0.88
    }
  ],
  "error": null,
  "processing_time": 0.42
}
```

## Advanced Usage

### Progress Callback

Monitor progress in real-time:

```python
def on_progress(batch_id, job):
    progress = (job.processed_count / job.total_count) * 100
    print(f"Progress: {progress:.1f}%")

processor.process_batch("batch_001", progress_callback=on_progress)
```

### Async Processing (Server)

Start batch and continue:

```bash
# Start batch (returns immediately)
curl -X POST http://localhost:8000/batch/batch_001/start

# Check status periodically
while true; do
  curl http://localhost:8000/batch/batch_001/status
  sleep 1
done

# Get results when done
curl http://localhost:8000/batch/batch_001/results
```

### Batch Chaining

Process multiple batches sequentially:

```python
batches = [
    ("batch_001", pdf_list_1),
    ("batch_002", pdf_list_2),
    ("batch_003", pdf_list_3),
]

for batch_id, pdf_paths in batches:
    job = processor.create_batch(batch_id, pdf_paths)
    result = processor.process_batch(batch_id)
    processor.export_results(batch_id, f"{batch_id}_results.json")
```

## Error Handling

### Failed PDFs

Individual failures don't stop the batch:

```python
results = processor.get_batch_results("batch_001")
for result in results:
    if not result.success:
        print(f"Failed: {result.pdf_path}")
        print(f"Error: {result.error}")
```

### Cleanup

Always cleanup resources:

```python
processor.cleanup()  # Shutdown thread pool
```

## Troubleshooting

### Slow Processing

1. Check if PDFs are too large or complex
2. Reduce techniques to essential ones
3. Increase worker count
4. Split into smaller batches

### High Memory Usage

1. Reduce worker count (fewer concurrent PDFs in memory)
2. Export results after each batch
3. Cleanup processor when done

### Uneven Load

Worker load may be uneven if:
- PDFs have different sizes
- Techniques take variable time
- System is under other load

This is normal - batch processor automatically load-balances.

## Integration with Frontend

The server handles batch operations automatically:

```javascript
// Frontend: Start batch analysis
const response = await fetch('/batch/create', {
  method: 'POST',
  body: JSON.stringify({
    batch_id: 'my_batch',
    document_ids: ['doc1', 'doc2', 'doc3'],
    techniques: ['bar_detector']
  })
});

// Start processing
await fetch('/batch/my_batch/start', { method: 'POST' });

// Poll for status
setInterval(async () => {
  const status = await fetch('/batch/my_batch/status').then(r => r.json());
  updateProgressBar(status.data.progress);
  
  if (status.data.status === 'completed') {
    const results = await fetch('/batch/my_batch/results').then(r => r.json());
    displayResults(results.data.results);
  }
}, 1000);
```

---

**Ready to process 1,000+ PDFs?** Start with `python batch_demo.py`
