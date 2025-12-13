"""
RAG Ingestion Router
====================
Handles ingestion of documents into RAGFlow.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import requests
from loguru import logger

from ragflow.client import get_ragflow_client

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])

class IngestRequest(BaseModel):
    url: str
    filename: str
    user_id: str

@router.post("/ingest")
async def ingest_document(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Ingest a document from a URL into RAGFlow for a specific user.
    Downloads the file and adds it to the user's personal vault.
    """
    try:
        # Download the file
        logger.info(f"Downloading {request.filename} from {request.url} for user {request.user_id}")
        response = requests.get(request.url)
        response.raise_for_status()
        content = response.content
        
        # Get RAG client
        client = get_ragflow_client()
        
        # Add to RAGFlow (this involves an async parse trigger, so it's relatively fast but blocking on upload)
        # We await it as it's an async method in our client wrapper
        success = await client.add_user_document(
            user_id=request.user_id,
            content=content,
            filename=request.filename
        )
        
        if success:
            return {"status": "success", "message": f"Ingested {request.filename}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add document to RAGFlow")

    except requests.RequestException as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to download file: {str(e)}")
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
