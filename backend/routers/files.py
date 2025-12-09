"""
File Management Router
======================
Upload files to RAGFlow for document processing and RAG.
RAGFlow handles storage, chunking, and embedding.
"""

from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from loguru import logger

from auth import get_current_user, UserData

router = APIRouter(prefix="/api/v1/files", tags=["Files"])


class FileUploadResponse(BaseModel):
    """Response after file upload"""
    success: bool
    filename: str
    message: str


class FileInfo(BaseModel):
    """File metadata"""
    filename: str
    doc_type: str
    uploaded_at: str


class ListFilesResponse(BaseModel):
    """List of user files"""
    files: List[FileInfo]
    total: int


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    doc_type: str = "document",
    user: UserData = Depends(get_current_user),
):
    """
    Upload file to RAGFlow for processing.
    
    RAGFlow will:
    1. Store the file
    2. Parse/OCR the content
    3. Chunk the document
    4. Generate embeddings
    5. Index for retrieval
    """
    try:
        from ragflow import get_ragflow_client
        
        client = get_ragflow_client()
        
        if not client.is_connected:
            raise HTTPException(
                status_code=503,
                detail="RAGFlow not available. Check RAGFLOW_API_KEY."
            )
        
        # Read file content
        content = await file.read()
        
        # Upload to RAGFlow
        success = await client.add_user_document(
            user_id=user.id,
            content=content, # Pass bytes directly
            filename=file.filename,
            doc_type=doc_type,
        )
        
        if success:
            logger.info(f"Uploaded {file.filename} to RAGFlow for user {user.id[:8]}")
            return FileUploadResponse(
                success=True,
                filename=file.filename,
                message="File uploaded and queued for processing"
            )
        else:
            raise HTTPException(status_code=500, detail="Upload failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=ListFilesResponse)
async def list_files(
    user: UserData = Depends(get_current_user),
):
    """
    List user's files in RAGFlow.
    
    Note: RAGFlow SDK may have limited list functionality.
    For full file management, access RAGFlow dashboard.
    """
    # RAGFlow SDK doesn't have a direct list method
    # Return empty for now - files are managed via RAGFlow UI
    return ListFilesResponse(
        files=[],
        total=0
    )


@router.post("/search")
async def search_files(
    query: str,
    limit: int = 5,
    user: UserData = Depends(get_current_user),
):
    """
    Search user's files using RAGFlow retrieval.
    
    Returns relevant document chunks matching the query.
    """
    try:
        from ragflow import get_ragflow_client
        
        client = get_ragflow_client()
        
        if not client.is_connected:
            raise HTTPException(
                status_code=503,
                detail="RAGFlow not available"
            )
        
        results = await client.search_user_context(
            user_id=user.id,
            query=query,
            limit=limit
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
