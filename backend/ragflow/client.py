"""
RAGFlow Client Wrapper for FlagPilot
=====================================
Provides a clean async interface to RAGFlow's SDK for knowledge base operations.
Based on: https://ragflow.io/docs/dev/python_api_reference
"""

from typing import Optional
from config import settings
import logging

# Import the official RAGFlow SDK
from ragflow_sdk import RAGFlow

logger = logging.getLogger(__name__)

# Singleton instance
_ragflow_client: Optional["RAGFlowClient"] = None


class RAGFlowClient:
    """
    Wrapper around RAGFlow SDK for FlagPilot.
    Provides async-compatible methods for knowledge base operations.
    """
    
    def __init__(self, api_key: str, base_url: str):
        """
        Initialize the RAGFlow client.
        
        Args:
            api_key: RAGFlow API key
            base_url: RAGFlow server URL (e.g., "http://ragflow:80")
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        
        # Initialize the official SDK client
        self._client = RAGFlow(api_key=api_key, base_url=base_url)
        
        logger.info(f"RAGFlowClient initialized with base_url: {base_url}")
    
    async def search_user_context(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        dataset_ids: Optional[list[str]] = None,
        similarity_threshold: float = 0.2
    ) -> list[dict]:
        """
        Search user's context (personal vault + global wisdom).
        
        Args:
            user_id: User ID for context (can be used to filter datasets)
            query: Search query
            limit: Maximum results to return
            dataset_ids: Optional list of dataset IDs to search
            similarity_threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            List of matching chunks as dictionaries
        """
        try:
            # If no dataset_ids provided, try to get all available datasets
            if not dataset_ids:
                datasets = self._client.list_datasets()
                dataset_ids = [ds.id for ds in datasets] if datasets else []
            
            if not dataset_ids:
                logger.warning("No datasets found for search")
                return []
            
            # Use RAGFlow's retrieve method
            # Note: The SDK's retrieve method is synchronous, but we wrap it for async compatibility
            chunks = self._client.retrieve(
                question=query,
                dataset_ids=dataset_ids,
                page_size=limit,
                similarity_threshold=similarity_threshold,
                top_k=limit * 10  # Get more candidates for better results
            )
            
            # Convert chunks to dictionaries
            results = []
            for chunk in chunks:
                results.append({
                    "content": getattr(chunk, "content", ""),
                    "document_name": getattr(chunk, "document_name", "Unknown"),
                    "document_id": getattr(chunk, "document_id", ""),
                    "dataset_id": getattr(chunk, "dataset_id", ""),
                    "similarity": getattr(chunk, "similarity", 0.0),
                    "id": getattr(chunk, "id", "")
                })
            
            logger.info(f"RAGFlow search returned {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"RAGFlow search error: {e}")
            return []
    
    async def retrieve(
        self,
        query: str,
        dataset_ids: Optional[list[str]] = None,
        limit: int = 5,
        similarity_threshold: float = 0.2
    ) -> list[dict]:
        """
        Retrieve chunks from datasets.
        
        Args:
            query: Search query
            dataset_ids: Optional list of dataset IDs
            limit: Maximum results
            similarity_threshold: Minimum similarity
            
        Returns:
            List of matching chunks
        """
        return await self.search_user_context(
            user_id="",  # Not used in this simple version
            query=query,
            limit=limit,
            dataset_ids=dataset_ids,
            similarity_threshold=similarity_threshold
        )
    
    def list_datasets(self) -> list:
        """List all available datasets."""
        try:
            return self._client.list_datasets()
        except Exception as e:
            logger.error(f"Failed to list datasets: {e}")
            return []
    
    def create_dataset(self, name: str, **kwargs):
        """Create a new dataset."""
        try:
            return self._client.create_dataset(name=name, **kwargs)
        except Exception as e:
            logger.error(f"Failed to create dataset: {e}")
            raise
    
    async def upload_document(
        self,
        dataset_id: str,
        filename: str,
        content: bytes
    ) -> bool:
        """
        Upload a document to a dataset.
        
        Args:
            dataset_id: Target dataset ID
            filename: Document filename
            content: Document content as bytes
            
        Returns:
            True if successful
        """
        try:
            datasets = self._client.list_datasets(id=dataset_id)
            if not datasets:
                logger.error(f"Dataset {dataset_id} not found")
                return False
            
            dataset = datasets[0]
            dataset.upload_documents([{
                "display_name": filename,
                "blob": content
            }])
            
            logger.info(f"Uploaded document {filename} to dataset {dataset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            return False
    
    async def health_check(self) -> dict:
        """Check RAGFlow connection health."""
        try:
            # Try to list datasets as a health check
            datasets = self._client.list_datasets(page_size=1)
            return {
                "status": "healthy",
                "connected": True,
                "dataset_count": len(datasets) if datasets else 0
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }


def get_ragflow_client() -> RAGFlowClient:
    """
    Get or create the singleton RAGFlow client.
    
    Returns:
        RAGFlowClient instance
    """
    global _ragflow_client
    
    if _ragflow_client is None:
        _ragflow_client = RAGFlowClient(
            api_key=settings.RAGFLOW_API_KEY or "",
            base_url=settings.RAGFLOW_URL
        )
    
    return _ragflow_client


def reset_ragflow_client():
    """Reset the singleton client (useful for testing)."""
    global _ragflow_client
    _ragflow_client = None
