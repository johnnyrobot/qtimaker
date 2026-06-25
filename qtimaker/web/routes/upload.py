# -*- coding: utf-8 -*-
#
# Document upload routes
#

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from ..config import UPLOAD_DIR, MAX_UPLOAD_SIZE
from ..services.docling_service import DoclingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Docling supports many formats; restrict uploads to this allowlist.
ALLOWED_EXTENSIONS = {
    # Documents
    '.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls',
    # Web/Markup
    '.html', '.htm', '.md', '.xml',
    # Images (for OCR)
    '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp',
    # Audio (for transcription)
    '.wav', '.mp3', '.m4a',
}

# Read uploads in bounded chunks so a large file can't exhaust memory.
_CHUNK_SIZE = 1024 * 1024  # 1 MB


@router.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF, PPT, Word, etc.) for parsing and question extraction.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Strip any path components from the client-supplied name to prevent
    # path traversal (e.g. "../../etc/passwd"); keep only the base name.
    safe_name = Path(file.filename).name
    file_ext = Path(safe_name).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "File type not supported. Supported formats: PDF, DOCX, PPTX, "
                "XLSX, HTML, images (PNG/JPG), audio (WAV/MP3)."
            ),
        )

    # Generate unique document ID and isolate each upload in its own directory.
    doc_id = str(uuid.uuid4())
    doc_dir = UPLOAD_DIR / doc_id
    doc_dir.mkdir(parents=True, exist_ok=True)

    file_path = doc_dir / safe_name

    # Stream to disk in chunks, enforcing the size limit as we go so we never
    # buffer an oversized upload entirely in memory.
    total = 0
    try:
        with file_path.open("wb") as out:
            while chunk := await file.read(_CHUNK_SIZE):
                total += len(chunk)
                if total > MAX_UPLOAD_SIZE:
                    out.close()
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="File too large")
                out.write(chunk)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to save uploaded file")
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    # Parse document using Docling.
    docling_service = DoclingService()
    try:
        parse_result = await docling_service.parse_document(str(file_path))
    except Exception:
        logger.exception("Document parsing failed for %s", doc_id)
        return JSONResponse(
            {
                "document_id": doc_id,
                "filename": safe_name,
                "status": "error",
                "error": "Document parsing failed.",
            },
            status_code=500,
        )

    return JSONResponse(
        {
            "document_id": doc_id,
            "filename": safe_name,
            "status": "parsed",
            "parse_result": parse_result,
            "message": "Document parsed successfully.",
        }
    )


@router.get("/documents/{document_id}/status")
async def get_document_status(document_id: str):
    """
    Get the status of a document processing job.
    """
    # Reject any id that isn't a bare UUID so it can't be used to probe the
    # filesystem outside the upload directory.
    try:
        uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document id")

    doc_dir = UPLOAD_DIR / document_id
    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    return {"document_id": document_id, "status": "processing"}
