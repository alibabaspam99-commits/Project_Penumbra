# Penumbra - Quick Start Guide

A distributed citizen science platform for recovering hidden text in redacted PDFs using advanced forensic techniques.

## What's Included

- **Frontend**: React/TypeScript PWA with 10 pages, 30+ UI components
- **Parser**: Python backend with 11 recovery techniques
- **Server**: FastAPI with PDF upload, analysis, and WebSocket streaming
- **Tests**: Comprehensive test suite with 200+ real EFTA PDFs

## System Architecture

```
Frontend (React PWA)
    ↓ (HTTP/WebSocket)
Backend Server (FastAPI)
    ↓ (Python)
Parser (11 Techniques)
    ↓
Analysis Results
```

## Quick Start (Local Development)

### 1. Install Dependencies

```bash
# Python backend
pip install -r backend_requirements.txt

# Frontend (in frontend directory)
cd frontend
npm install
npm run build
cd ..
```

### 2. Run the Server

```bash
python server.py
```

Server will start on `http://localhost:8000`

### 3. Open in Browser

```
http://localhost:8000
```

## Available Scripts

### Demo - Test Parser on Real PDFs

Analyzes EFTA fixtures with all 11 techniques:

```bash
# Analyze first 3 test PDFs (auto)
python demo.py

# Analyze specific PDF
python demo.py tests/fixtures/EFTA00009890.pdf
```

Output: `demo_results.json`

### Integration Tests - Test Server API

Tests all HTTP endpoints:

```bash
# Start server first
python server.py

# In another terminal
python test_server_integration.py
```

Tests:
- Health check
- PDF upload
- Document listing
- Analysis execution
- Results retrieval
- User profile
- Leaderboard

## 11 Recovery Techniques

1. **OCG Layer Extraction** - Toggle hidden PDF layers
2. **Text Layer Extraction** - Extract hidden text beneath redactions
3. **Bar Detector** - Identify redaction bars with dark pixel clustering
4. **Image Extractor** - Extract images from PDFs
5. **Over-redaction Analysis** - Search string attacks on visible text
6. **Width Filter** - Eliminate candidates by text width matching
7. **Edge Extractor** - Sub-pixel gradient analysis
8. **Font Metrics** - Font calibration from document
9. **Character Edge Matcher** - First/last character edge matching
10. **Full Edge Matcher** - Full edge signature template matching
11. **OCR Text Extraction** - Tesseract OCR with bounding boxes

## API Endpoints

### Document Management
- `POST /documents/upload` - Upload PDF
- `GET /documents` - List documents
- `DELETE /documents/{id}` - Delete document

### Analysis
- `POST /documents/{id}/analyze` - Run analysis
- `GET /documents/{id}/analysis` - Get results
- `GET /analysis/{id}/status` - Check progress

### Info
- `GET /api/techniques` - List available techniques
- `GET /user/profile` - User profile
- `GET /user/stats` - User statistics
- `GET /leaderboard` - Leaderboard
- `GET /health` - Health check

### WebSocket
- `WS /ws/analyze` - Stream analysis results in real-time

## Test Data

200+ real EFTA PDFs available in:
- `tests/fixtures/EFTA*.pdf` - Individual PDFs
- `tests/fixtures/DataSet 12/IMAGES/0001/` - Large dataset

## Project Structure

```
├── frontend/                 # React PWA
│   ├── src/
│   │   ├── components/      # 30+ UI components
│   │   ├── pages/           # 6 main pages
│   │   ├── api/             # HTTP client
│   │   └── store/           # Zustand state management
│   ├── dist/                # Built files (after npm run build)
│   └── package.json
│
├── parser/                   # Python parser
│   ├── core/               # Framework (coordinator, document, results)
│   ├── techniques/         # 11 recovery techniques
│   └── requirements.txt
│
├── tests/                    # Test suite
│   ├── core/               # Framework tests
│   ├── techniques/         # Technique tests
│   └── fixtures/           # 200+ real PDFs
│
├── server.py               # FastAPI server
├── demo.py                 # Parser demo
├── test_server_integration.py  # API tests
└── QUICKSTART.md          # This file
```

## Development Workflow

### 1. Make Changes to Parser

```bash
# Edit parser/techniques/*.py
# Changes are live in demo.py and server.py
python demo.py
```

### 2. Make Changes to Frontend

```bash
cd frontend
npm run dev  # Hot reload dev server

# When ready to deploy:
npm run build
```

### 3. Test Everything Together

```bash
# Terminal 1: Start server
python server.py

# Terminal 2: Run integration tests
python test_server_integration.py
```

## Troubleshooting

### Tesseract OCR Not Found

If you see "Tesseract OCR not installed":

**Linux:**
```bash
apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
- Download installer: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH

### Module Not Found

If you see "No module named 'parser'":

```bash
# Make sure you're in the project root, not in frontend/
cd /path/to/Project_Penumbra/.worktrees/impl-core-parser
```

### Port 8000 Already in Use

```bash
# Use a different port
python server.py --port 8001
```

## Next Steps

### For Frontend Development
- Customize pages in `frontend/src/pages/`
- Add components in `frontend/src/components/`
- Update store in `frontend/src/store/appStore.ts`

### For Parser Development
- Add new techniques in `parser/techniques/`
- Extend coordinator in `parser/core/coordinator.py`
- Add tests in `tests/techniques/`

### For Server Development
- Add endpoints in `server.py`
- Add authentication (currently placeholder)
- Add database persistence (currently in-memory)

## Performance Notes

- **Frontend**: 111 modules, 33.85 kB CSS, 190.92 kB JS (production build)
- **Parser**: ~0.5-2 seconds per technique per page
- **Server**: Handles streaming WebSocket for real-time results

## Architecture Decisions

1. **Modular Techniques**: Each recovery method is independent, can be run/combined flexibly
2. **In-Memory Storage**: Simple server suitable for demos; add database for production
3. **PWA**: Works offline, installable on mobile phones
4. **No OCR by default**: Tesseract optional, other 10 techniques work without it
5. **Worktree-based**: Isolated development environment from main repo

## Resources

- **CLAUDE.md** - Project context and guidelines
- **docs/plans/** - Implementation plans and strategies
- **tests/fixtures/** - Real EFTA PDFs for validation

---

**Ready to get started?**

```bash
python server.py
# Open http://localhost:8000
```
