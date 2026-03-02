"""
Penumbra FastAPI Server
Connects frontend to parser, manages PDF uploads and analysis streaming
"""

import asyncio
import os
import shutil
from pathlib import Path
from typing import Optional
import json

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from parser.core.document import PDFDocument
from parser.core.coordinator import ParserCoordinator
from parser.core.results import PDFProcessingReport
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

# Create FastAPI app
app = FastAPI(
    title="Penumbra Parser API",
    description="Backend API for redaction analysis",
    version="0.1.0"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for uploaded files
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory storage for analysis results
analysis_results = {}
document_registry = {}

# Initialize parser coordinator
coordinator = ParserCoordinator()

# Register all techniques
coordinator.register_technique(OCGLayerExtractor())
coordinator.register_technique(TextLayerExtractor())
coordinator.register_technique(BarDetector())
coordinator.register_technique(ImageExtractor())
coordinator.register_technique(OverRedactionAnalyzer())
coordinator.register_technique(WidthFilter())
coordinator.register_technique(EdgeExtractor())
coordinator.register_technique(FontMetricsAnalyzer())
coordinator.register_technique(CharacterEdgeMatcher())
coordinator.register_technique(FullEdgeSignatureMatcher())
coordinator.register_technique(OCRTextExtraction())


@app.get("/")
async def root():
    """Root endpoint - return API info"""
    return {
        "name": "Penumbra Parser API",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "upload": "POST /api/upload",
            "analyze": "POST /api/analyze/{document_id}",
            "results": "GET /api/results/{analysis_id}",
            "documents": "GET /api/documents",
            "techniques": "GET /api/techniques"
        }
    }


@app.get("/api/techniques")
async def get_techniques():
    """Get list of available techniques"""
    return {
        "techniques": list(coordinator.techniques.keys()),
        "count": len(coordinator.techniques)
    }


@app.post("/documents/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file for analysis"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Register document
        doc_id = file.filename.replace('.pdf', '')
        document_registry[doc_id] = {
            "filename": file.filename,
            "path": str(file_path),
            "size": len(content),
            "status": "uploaded"
        }
        
        return {
            "success": True,
            "data": {
                "document_id": doc_id,
                "filename": file.filename
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents(skip: int = 0, limit: int = 20):
    """Get list of uploaded documents"""
    docs = list(document_registry.values())
    return {
        "success": True,
        "data": {
            "documents": docs[skip:skip+limit],
            "total": len(docs)
        }
    }


@app.post("/documents/{document_id}/analyze")
async def analyze_pdf(document_id: str, request_data: dict = None):
    """
    Analyze a PDF with selected techniques
    Returns analysis_id that can be used to fetch results
    """
    try:
        # Get document
        if document_id not in document_registry:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_info = document_registry[document_id]
        pdf_path = doc_info["path"]
        
        # Get techniques from request
        techniques = request_data.get("techniques") if request_data else None
        if techniques is None:
            techniques = list(coordinator.techniques.keys())
        
        # Open PDF
        doc = PDFDocument(pdf_path)
        
        # Create analysis ID
        import time
        analysis_id = f"{document_id}_{int(time.time())}"
        
        # Process each page
        results = []
        total_pages = doc.page_count
        
        for page_num in range(total_pages):
            page = doc._doc[page_num]
            
            # Run selected techniques
            page_results = coordinator.run_page(
                page=page,
                pdf_document=doc,
                selected_techniques=techniques
            )
            
            results.append({
                "page": page_num + 1,
                "technique_results": [
                    {
                        "technique": r.technique_name,
                        "success": r.success,
                        "confidence": r.confidence,
                        "error": r.error
                    }
                    for r in page_results
                ]
            })
        
        doc.close()
        
        # Store analysis results
        analysis_results[analysis_id] = {
            "document_id": document_id,
            "status": "completed",
            "pages_analyzed": total_pages,
            "techniques_used": techniques,
            "results": results,
            "timestamp": str(Path(pdf_path).stat().st_mtime)
        }
        
        # Update document status
        document_registry[document_id]["status"] = "analyzed"
        
        return {
            "success": True,
            "data": {
                "analysis_id": analysis_id,
                "document_id": document_id,
                "status": "completed"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/{document_id}/analysis")
async def get_analysis_results(document_id: str):
    """Get analysis results for a document"""
    try:
        # Find analysis results for this document
        doc_results = [v for k, v in analysis_results.items() 
                      if v["document_id"] == document_id]
        
        if not doc_results:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "success": True,
            "data": doc_results[-1]  # Return most recent analysis
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """Get analysis status"""
    try:
        if analysis_id not in analysis_results:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        result = analysis_results[analysis_id]
        return {
            "success": True,
            "data": {
                "status": result["status"],
                "progress": 100 if result["status"] == "completed" else 0
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """
    WebSocket endpoint for streaming analysis results
    
    Client sends: {"document_id": "...", "techniques": [...]}
    Server streams: {"page": N, "technique": "...", "progress": X%}
    """
    await websocket.accept()
    try:
        # Receive analysis request
        data = await websocket.receive_json()
        document_id = data.get("document_id")
        techniques = data.get("techniques", list(coordinator.techniques.keys()))
        
        # Validate document
        if document_id not in document_registry:
            await websocket.send_json({"error": "Document not found"})
            await websocket.close()
            return
        
        doc_info = document_registry[document_id]
        pdf_path = doc_info["path"]
        
        # Open PDF
        doc = PDFDocument(pdf_path)
        total_pages = doc.page_count
        
        # Process each page and stream results
        for page_num in range(total_pages):
            page = doc._doc[page_num]
            
            # Run techniques
            page_results = coordinator.run_page(
                page=page,
                pdf_document=doc,
                selected_techniques=techniques
            )
            
            # Stream each technique result
            for result in page_results:
                await websocket.send_json({
                    "page": page_num + 1,
                    "total_pages": total_pages,
                    "technique": result.technique_name,
                    "success": result.success,
                    "confidence": result.confidence,
                    "progress": int((page_num / total_pages) * 100)
                })
            
            # Small delay to allow frontend to process
            await asyncio.sleep(0.1)
        
        doc.close()
        
        # Send completion message
        await websocket.send_json({
            "status": "completed",
            "pages_analyzed": total_pages,
            "message": "Analysis complete"
        })
    
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete an uploaded document"""
    try:
        if document_id not in document_registry:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_info = document_registry[document_id]
        pdf_path = Path(doc_info["path"])
        
        # Delete file
        if pdf_path.exists():
            pdf_path.unlink()
        
        # Remove from registry
        del document_registry[document_id]
        
        # Remove associated analysis results
        to_delete = [k for k, v in analysis_results.items() 
                     if v["document_id"] == document_id]
        for k in to_delete:
            del analysis_results[k]
        
        return {
            "success": True,
            "data": {"success": True}
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# User endpoints (placeholder - no auth in simple server)
@app.get("/user/profile")
async def get_user_profile():
    """Get current user profile"""
    return {
        "success": True,
        "data": {
            "id": "demo_user",
            "username": "demo_user",
            "email": "demo@penumbra.local",
            "avatar_url": None
        }
    }


@app.put("/user/profile")
async def update_user_profile(data: dict):
    """Update user profile"""
    return {
        "success": True,
        "data": {"updated": True}
    }


@app.get("/user/stats")
async def get_user_stats():
    """Get user statistics"""
    doc_count = len(document_registry)
    analysis_count = len(analysis_results)
    
    return {
        "success": True,
        "data": {
            "total_pdfs_processed": doc_count,
            "total_redactions_analyzed": analysis_count,
            "verified_count": 0,
            "accuracy": 0.95,
            "current_streak": 0,
            "best_streak": 0,
            "total_points": doc_count * 10,
            "level": 1 + (doc_count // 10),
            "rank": "contributor"
        }
    }


# Leaderboard endpoints (placeholder)
@app.get("/leaderboard")
async def get_leaderboard(limit: int = 100):
    """Get leaderboard"""
    return {
        "success": True,
        "data": [
            {
                "rank": 1,
                "user_id": "demo_user",
                "username": "demo_user",
                "points": 150,
                "pdfs_processed": 15,
                "accuracy": 0.98
            }
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "documents": len(document_registry),
            "analyses": len(analysis_results),
            "techniques": len(coordinator.techniques)
        }
    }


# Serve frontend static files if available
frontend_dist = Path("./frontend/dist")
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    print("Starting Penumbra Parser API Server...")
    print("Frontend: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("WebSocket: ws://localhost:8000/ws/analyze")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
