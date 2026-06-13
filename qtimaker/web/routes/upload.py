# -*- coding: utf-8 -*-
#
# Document upload routes
#

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import uuid
from pathlib import Path
from ..config import UPLOAD_DIR, MAX_UPLOAD_SIZE
from ..services.docling_service import DoclingService

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF, PPT, Word) for parsing and question extraction.
    """
    # Validate file type - Docling supports many formats
    allowed_extensions = {
        # Documents
        '.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls',
        # Web/Markup
        '.html', '.htm', '.md', '.xml',
        # Images (for OCR)
        '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp',
        # Audio (for transcription)
        '.wav', '.mp3', '.m4a'
    }
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Docling supports: PDF, DOCX, PPTX, XLSX, HTML, images (PNG/JPG), audio (WAV/MP3)"
        )
    
    # Generate unique document ID
    doc_id = str(uuid.uuid4())
    doc_dir = UPLOAD_DIR / doc_id
    doc_dir.mkdir(exist_ok=True)
    
    # Save uploaded file
    file_path = doc_dir / file.filename
    content = await file.read()
    
    # Check file size
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    file_path.write_bytes(content)
    
    # Parse document using Docling
    docling_service = DoclingService()
    try:
        parse_result = await docling_service.parse_document(str(file_path))
        
        # Store document in database
        from ..services.database.postgres import NeonPostgresService
        postgres = NeonPostgresService()
        await postgres.store_document(doc_id, file.filename, str(file_path), file_ext)
        
        # Trigger question extraction (async, can be done in background)
        from ..services.rag_service import RAGService
        rag_service = RAGService()
        # TODO: Extract questions from parsed content
        # questions = await rag_service.extract_questions_from_document(doc_id, parse_result.get('chunks', []))
        
        return JSONResponse({
            "document_id": doc_id,
            "filename": file.filename,
            "status": "parsed",
            "parse_result": parse_result,
            "message": "Document parsed successfully. Question extraction can be triggered separately."
        })
    except Exception as e:
        return JSONResponse({
            "document_id": doc_id,
            "filename": file.filename,
            "status": "error",
            "error": str(e)
        }, status_code=500)


@router.get("/documents/{document_id}/status")
async def get_document_status(document_id: str):
    """
    Get the status of a document processing job.
    """
    doc_dir = UPLOAD_DIR / document_id
    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    # TODO: Check processing status from database
    return {"document_id": document_id, "status": "processing"}

