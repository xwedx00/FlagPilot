"""
RAG Router for FlagPilot v7.0
=============================
Document ingestion and retrieval using Qdrant + MinIO.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from loguru import logger

from lib.rag import get_rag_pipeline
from lib.vectorstore import get_qdrant_store
from lib.storage import get_minio_storage

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])


# ===========================================
# Request/Response Models
# ===========================================

class IngestTextRequest(BaseModel):
    text: str
    source: str = "user_input"
    user_id: Optional[str] = None
    metadata: Optional[dict] = None


class IngestURLRequest(BaseModel):
    url: str
    user_id: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    k: int = 5
    user_id: Optional[str] = None


class SearchResult(BaseModel):
    content: str
    source: str
    score: Optional[float] = None
    metadata: dict = {}


# ===========================================
# Endpoints
# ===========================================

@router.post("/ingest/text")
async def ingest_text(request: IngestTextRequest):
    """
    Ingest plain text into the RAG system.
    Text is chunked and embedded into Qdrant.
    """
    try:
        pipeline = get_rag_pipeline()
        result = await pipeline.ingest_text(
            text=request.text,
            source=request.source,
            user_id=request.user_id,
            metadata=request.metadata,
        )
        
        if result.get("success"):
            return {
                "status": "success",
                "chunk_count": result["chunk_count"],
                "source": result["source"],
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        logger.error(f"Text ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
):
    """
    Ingest a file into the RAG system.
    File is stored in MinIO and embedded into Qdrant.
    """
    try:
        pipeline = get_rag_pipeline()
        result = await pipeline.ingest_file(
            file_data=file.file,
            file_name=file.filename,
            content_type=file.content_type or "application/octet-stream",
            user_id=user_id,
        )
        
        if result.get("success"):
            return {
                "status": "success",
                "chunk_count": result["chunk_count"],
                "file": result.get("file"),
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except Exception as e:
        logger.error(f"File ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[SearchResult])
async def search_documents(request: SearchRequest):
    """
    Search for relevant documents using semantic similarity.
    """
    try:
        pipeline = get_rag_pipeline()
        results = await pipeline.retrieve_with_scores(
            query=request.query,
            k=request.k,
        )
        
        return [
            SearchResult(
                content=doc.page_content,
                source=doc.metadata.get("source", "unknown"),
                score=score,
                metadata=doc.metadata,
            )
            for doc, score in results
        ]
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collection/info")
async def get_collection_info():
    """Get Qdrant collection statistics"""
    try:
        qdrant = get_qdrant_store()
        info = qdrant.get_collection_info()
        return info
    except Exception as e:
        logger.error(f"Failed to get collection info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def list_files(prefix: str = "", user_id: Optional[str] = None):
    """List files in MinIO storage"""
    try:
        minio = get_minio_storage()
        files = minio.list_files(prefix=prefix or (user_id + "/" if user_id else ""))
        return {"files": files}
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{object_name:path}/url")
async def get_file_url(object_name: str, expires: int = 3600):
    """Get presigned URL for file download"""
    try:
        minio = get_minio_storage()
        url = minio.get_presigned_url(object_name, expires=expires)
        return {"url": url}
    except Exception as e:
        logger.error(f"Failed to get file URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))
