# WebSocket Real-Time Streaming

Stream analysis results in real-time as they're processed.

## Overview

Instead of waiting for analysis to complete, WebSocket allows:
- **Real-time feedback** - Results appear as techniques complete
- **Progress tracking** - Live % updates
- **Better UX** - Users see work happening in real-time
- **Cancellation** - Stop analysis at any time
- **Low latency** - Minimal network overhead

## Architecture

```
Frontend
  ↓ (WebSocket)
Server (processes PDF)
  ↓ (streaming messages)
Frontend (displays results in real-time)
```

## Message Types

### Client → Server (Request)

```json
{
  "document_id": "EFTA00009890",
  "techniques": ["bar_detector", "text_layer"],
  "analysis_id": "analysis_12345"
}
```

### Server → Client (Responses)

#### Start Message
```json
{
  "type": "start",
  "analysis_id": "analysis_12345",
  "document_id": "EFTA00009890",
  "techniques_count": 2
}
```

#### Document Info
```json
{
  "type": "document_info",
  "total_pages": 5,
  "page_count": 5
}
```

#### Page Start
```json
{
  "type": "page_start",
  "page": 1,
  "total_pages": 5
}
```

#### Technique Result (Streams for each technique)
```json
{
  "type": "technique_result",
  "page": 1,
  "technique": "bar_detector",
  "success": true,
  "confidence": 0.923,
  "error": null
}
```

#### Page Complete
```json
{
  "type": "page_complete",
  "page": 1,
  "total_pages": 5,
  "progress": 20,
  "techniques_succeeded": 2,
  "techniques_total": 2
}
```

#### Completion
```json
{
  "type": "complete",
  "analysis_id": "analysis_12345",
  "pages_analyzed": 5,
  "total_time": 3.42,
  "techniques_run": 2,
  "total_results": 10,
  "successful_results": 9,
  "success_rate": "90.0%",
  "status": "completed"
}
```

#### Error
```json
{
  "type": "error",
  "error": "Document not found",
  "analysis_id": "analysis_12345"
}
```

## Usage

### Python Client

```bash
python ws_client_demo.py
```

### JavaScript/TypeScript (Frontend)

```typescript
import { apiMethods } from '@/api/client'

// Start streaming analysis
const closeConnection = apiMethods.streamAnalysis(
  documentId,
  ['bar_detector', 'text_layer'],
  
  // onMessage callback - received each message
  (data) => {
    if (data.type === 'start') {
      console.log('Analysis started')
    } else if (data.type === 'technique_result') {
      console.log(`${data.technique}: ${data.success ? 'OK' : 'FAIL'}`)
      updateUI(data)
    } else if (data.type === 'page_complete') {
      updateProgressBar(data.progress)
    } else if (data.type === 'complete') {
      showResults(data)
    }
  },
  
  // onError callback
  (error) => {
    console.error('WebSocket error:', error)
    showErrorNotification(error)
  },
  
  // onComplete callback
  () => {
    console.log('Connection closed')
  }
)

// Later: close the connection if needed
closeConnection()
```

### React Component Example

```typescript
import { useState, useCallback } from 'react'
import { apiMethods } from '@/api/client'

export function AnalysisWithStreaming({ documentId }) {
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState<any[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  
  const startAnalysis = useCallback(() => {
    setIsAnalyzing(true)
    setResults([])
    
    const close = apiMethods.streamAnalysis(
      documentId,
      ['bar_detector', 'image_extractor', 'text_layer'],
      
      (data) => {
        if (data.type === 'page_complete') {
          setProgress(data.progress)
        } else if (data.type === 'technique_result') {
          setResults(prev => [...prev, data])
        } else if (data.type === 'complete') {
          setIsAnalyzing(false)
          setProgress(100)
        }
      },
      
      (error) => {
        console.error(error)
        setIsAnalyzing(false)
      },
      
      () => {
        setIsAnalyzing(false)
      }
    )
    
    // Store close function in state if you need to cancel
    return close
  }, [documentId])
  
  return (
    <div>
      <button onClick={startAnalysis} disabled={isAnalyzing}>
        {isAnalyzing ? 'Analyzing...' : 'Start Analysis'}
      </button>
      
      <ProgressBar value={progress} />
      
      <ResultsList items={results} />
    </div>
  )
}
```

## HTTP Fallback

If WebSocket is not available:

```typescript
// Fallback to HTTP polling
const { data } = await apiMethods.analyzeDocument(documentId, techniques)
const analysisId = data.analysis_id

// Poll for results
const pollResults = setInterval(async () => {
  const status = await apiMethods.getAnalysisStatus(analysisId)
  updateUI(status.data)
  
  if (status.data.status === 'completed') {
    clearInterval(pollResults)
  }
}, 1000)
```

## Performance

### Latency
- Page start to first result: ~50-100ms
- Between technique results: ~5-10ms
- Full page processing: ~200-500ms (depends on techniques)

### Throughput
- ~50-100 messages per PDF (varies with page count)
- Network bandwidth: < 1MB per 100 PDFs
- Memory per connection: ~1-2MB

### Scaling

With concurrent connections (batch processing):
- 1 connection: 1 WebSocket open
- 4 connections: 4 WebSockets open (batch processor with 4 workers)
- Multiple clients: Shared server connection pool

## Browser Compatibility

WebSocket support:
- ✅ Chrome/Edge 16+
- ✅ Firefox 11+
- ✅ Safari 7+
- ✅ iOS Safari 7+
- ✅ Android Browser 4.4+

For older browsers, use HTTP fallback (polling).

## Security

### Authentication

Add auth token to WebSocket:

```typescript
const ws = new WebSocket(wsUrl)
ws.onopen = () => {
  const token = localStorage.getItem('auth_token')
  ws.send(JSON.stringify({
    type: 'auth',
    token: token,
    ...analysisRequest
  }))
}
```

### CORS

WebSocket doesn't use CORS, but ensure:
- Same origin for same-site requests
- Proper origin headers for cross-origin

## Debugging

### Monitor in DevTools

```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/ws/analyze')
ws.onmessage = (e) => console.log(JSON.parse(e.data))
ws.send(JSON.stringify({
  document_id: 'test',
  techniques: ['bar_detector']
}))
```

### Server Logging

WebSocket messages are logged if you run with debug:

```bash
PYTHONUNBUFFERED=1 python server.py
```

Watch for:
- Connection open/close
- Message send/receive
- Errors and exceptions

## Optimization Tips

1. **Batch techniques** - Run 2-4 techniques per analysis
2. **Progressive display** - Show results as they arrive
3. **Debounce updates** - Don't update UI for every result
4. **Cancel long runs** - Give users ability to stop analysis
5. **Reconnect on failure** - Auto-reconnect with exponential backoff

## Common Issues

### Connection Refused

**Problem:** `WebSocket connection failed`

**Solution:**
- Check server is running on localhost:8000
- Check firewall isn't blocking WebSocket
- Verify browser supports WebSocket

### Timeout

**Problem:** Connection drops after N seconds

**Solution:**
- Add keep-alive messages every 30 seconds
- Increase server timeout if needed
- Check for network/proxy timeout settings

### Duplicate Results

**Problem:** Same technique result received twice

**Solution:**
- Browser tab open twice (disable one)
- Reconnect happened during processing (normal)
- Check server isn't sending duplicates

## API Reference

### `streamAnalysis()`

```typescript
streamAnalysis(
  documentId: string,           // PDF to analyze
  techniques: string[],         // Which techniques to run
  onMessage: (data) => void,   // Receives all messages
  onError: (error) => void,    // Error handler
  onComplete: () => void       // Connection closed
) => () => void                // Returns function to close connection
```

---

**Ready to stream real-time results?** Run the demo:
```bash
python server.py        # Terminal 1
python ws_client_demo.py # Terminal 2
```
