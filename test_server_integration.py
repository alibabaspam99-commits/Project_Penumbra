#!/usr/bin/env python
"""
Integration tests for Penumbra API Server
Tests the full HTTP API and WebSocket endpoints
"""

import asyncio
import json
import tempfile
from pathlib import Path
import httpx
import asyncio


async def test_server_health():
    """Test health check endpoint."""
    print("\n[TEST] Server Health Check")
    print("-" * 40)
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            response = await client.get("/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Health check passed")
                print(f"  Status: {data.get('data', {}).get('status')}")
                return True
        except Exception as e:
            print(f"✗ Health check failed: {str(e)}")
            return False


async def test_pdf_upload():
    """Test PDF upload endpoint."""
    print("\n[TEST] PDF Upload")
    print("-" * 40)
    
    # Find a test PDF
    test_pdf = Path("tests/fixtures/EFTA00009890.pdf")
    if not test_pdf.exists():
        print(f"✗ Test PDF not found: {test_pdf}")
        return None
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            with open(test_pdf, "rb") as f:
                files = {"file": ("test.pdf", f, "application/pdf")}
                response = await client.post("/documents/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                doc_id = data.get("data", {}).get("document_id")
                print(f"✓ PDF uploaded successfully")
                print(f"  Document ID: {doc_id}")
                return doc_id
            else:
                print(f"✗ Upload failed: {response.status_code}")
                print(f"  {response.text}")
                return None
        except Exception as e:
            print(f"✗ Upload error: {str(e)}")
            return None


async def test_list_documents():
    """Test document listing endpoint."""
    print("\n[TEST] List Documents")
    print("-" * 40)
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            response = await client.get("/documents")
            if response.status_code == 200:
                data = response.json()
                docs = data.get("data", {}).get("documents", [])
                print(f"✓ Documents listed successfully")
                print(f"  Total documents: {len(docs)}")
                return True
            else:
                print(f"✗ Listing failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Listing error: {str(e)}")
            return False


async def test_get_techniques():
    """Test techniques endpoint."""
    print("\n[TEST] Get Techniques")
    print("-" * 40)
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            response = await client.get("/api/techniques")
            if response.status_code == 200:
                data = response.json()
                techniques = data.get("techniques", [])
                print(f"✓ Techniques retrieved successfully")
                print(f"  Total techniques: {len(techniques)}")
                for tech in sorted(techniques):
                    print(f"    - {tech}")
                return True
            else:
                print(f"✗ Request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False


async def test_analyze_document(doc_id):
    """Test document analysis endpoint."""
    print(f"\n[TEST] Analyze Document ({doc_id})")
    print("-" * 40)
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            payload = {
                "techniques": [
                    "bar_detector",
                    "image_extractor",
                    "text_layer"
                ]
            }
            response = await client.post(
                f"/documents/{doc_id}/analyze",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis_id = data.get("data", {}).get("analysis_id")
                print(f"✓ Analysis started successfully")
                print(f"  Analysis ID: {analysis_id}")
                return analysis_id
            else:
                print(f"✗ Analysis failed: {response.status_code}")
                print(f"  {response.text}")
                return None
        except Exception as e:
            print(f"✗ Analysis error: {str(e)}")
            return None


async def test_get_analysis_results(analysis_id):
    """Test analysis results endpoint."""
    print(f"\n[TEST] Get Analysis Results ({analysis_id})")
    print("-" * 40)
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            response = await client.get(f"/analysis/{analysis_id}/status")
            if response.status_code == 200:
                data = response.json()
                status = data.get("data", {}).get("status")
                progress = data.get("data", {}).get("progress")
                print(f"✓ Results retrieved successfully")
                print(f"  Status: {status}")
                print(f"  Progress: {progress}%")
                return True
            else:
                print(f"✗ Request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False


async def test_user_profile():
    """Test user profile endpoint."""
    print("\n[TEST] User Profile")
    print("-" * 40)
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            response = await client.get("/user/profile")
            if response.status_code == 200:
                data = response.json()
                user = data.get("data", {})
                print(f"✓ Profile retrieved successfully")
                print(f"  Username: {user.get('username')}")
                print(f"  Email: {user.get('email')}")
                return True
            else:
                print(f"✗ Request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False


async def test_leaderboard():
    """Test leaderboard endpoint."""
    print("\n[TEST] Leaderboard")
    print("-" * 40)
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            response = await client.get("/leaderboard")
            if response.status_code == 200:
                data = response.json()
                entries = data.get("data", [])
                print(f"✓ Leaderboard retrieved successfully")
                print(f"  Top entries: {len(entries)}")
                for entry in entries[:3]:
                    print(f"    {entry.get('rank')}. {entry.get('username')} - {entry.get('points')} pts")
                return True
            else:
                print(f"✗ Request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False


async def main():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("PENUMBRA SERVER INTEGRATION TESTS")
    print("=" * 60)
    print("\nMake sure server is running: python server.py")
    
    results = {}
    
    # Test 1: Health check
    results["health"] = await test_server_health()
    
    if not results["health"]:
        print("\n✗ Server is not running. Start with: python server.py")
        return
    
    # Test 2: Get techniques
    results["techniques"] = await test_get_techniques()
    
    # Test 3: Upload PDF
    doc_id = await test_pdf_upload()
    results["upload"] = doc_id is not None
    
    # Test 4: List documents
    results["list"] = await test_list_documents()
    
    # Test 5: Analyze document
    if doc_id:
        analysis_id = await test_analyze_document(doc_id)
        results["analyze"] = analysis_id is not None
        
        # Test 6: Get results
        if analysis_id:
            results["results"] = await test_get_analysis_results(analysis_id)
    
    # Test 7: User profile
    results["profile"] = await test_user_profile()
    
    # Test 8: Leaderboard
    results["leaderboard"] = await test_leaderboard()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✓ PASS" if passed_flag else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")


if __name__ == "__main__":
    print("\nStarting integration tests...")
    print("(Server should be running on localhost:8000)")
    
    asyncio.run(main())
