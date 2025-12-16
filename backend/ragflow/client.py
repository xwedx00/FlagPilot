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
            user_id: User ID for context (used to find personal dataset)
            query: Search query
            limit: Maximum results to return
            dataset_ids: Optional list of dataset IDs to search (overrides auto-discovery)
            similarity_threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            List of matching chunks as dictionaries
        """
        try:
            target_datasets = []
            
            # Smart Thresholding: Lower threshold for longer queries as they are harder to match exactly
            adjusted_threshold = similarity_threshold
            if len(query) > 100:
                adjusted_threshold = max(0.1, similarity_threshold - 0.05)
                logger.debug(f"Long query detected ({len(query)} chars). Lowering threshold to {adjusted_threshold}")

            # 1. Determine Target Datasets
            if dataset_ids:
                target_datasets = dataset_ids
            else:
                # Auto-discovery strategy
                all_datasets = self.list_datasets()
                if not all_datasets:
                    logger.warning("No datasets available in RAGFlow.")
                    return []
                
                # Filter for User's Personal Dataset AND Global Wisdom
                # Convention: Personal = "{user_id}", Global = "global_wisdom"
                for ds in all_datasets:
                    ds_name = getattr(ds, "name", "").lower()
                    
                    # Match User ID (Personal Vault)
                    if user_id and user_id.lower() in ds_name:
                        target_datasets.append(ds.id)
                    
                    # Match Global Wisdom
                    if "global_wisdom" in ds_name or "flagpilot_global" in ds_name:
                        target_datasets.append(ds.id)
                
                # Fallback: If no specific datasets found, search ALL (be careful with this in prod)
                if not target_datasets and all_datasets:
                    # logger.info("No specific datasets found for user/global. Falling back to searching all datasets (DEV MODE).")
                    target_datasets = [ds.id for ds in all_datasets]

            if not target_datasets:
                logger.warning(f"No target datasets identified for user {user_id}")
                return []
            
            logger.info(f"Searching Datasets: {target_datasets} | Query: '{query[:50]}...'")

            # 2. Execute Search (Async Wrap)
            # RAGFlow SDK retrieve is blocking, so we ideally run it in an executor if high load,
            # but for now direct call is acceptable in this async wrapper.
            
            chunks = self._client.retrieve(
                question=query,
                dataset_ids=target_datasets,
                page_size=limit,
                similarity_threshold=adjusted_threshold,
                vector_similarity_weight=0.7, # Higher weight on vector for semantic meaning
                top_k=1024
            )
            
            # 3. Format Results
            results = []
            if chunks:
                for chunk in chunks:
                    results.append({
                        "content": getattr(chunk, "content_with_weight", getattr(chunk, "content", "")),
                        "document_name": getattr(chunk, "document_name", "Unknown"),
                        "document_id": getattr(chunk, "document_id", ""),
                        "dataset_id": getattr(chunk, "dataset_id", ""),
                        "similarity": getattr(chunk, "similarity", 0.0),
                        "id": getattr(chunk, "id", "")
                    })
            
            logger.info(f"RAGFlow search complete. Found {len(results)} chunks.")
            return results
            
        except Exception as e:
            logger.exception(f"CRITICAL RAGFlow Search Error: {e}")
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

    def reset_system(self):
        """
        DANGER: Deletes ALL datasets.
        Used ONLY for clean system tests.
        """
        try:
            datasets = self.list_datasets()
            if not datasets:
                return
            
            ids = [ds.id for ds in datasets]
            logger.warning(f"RESET SYSTEM: Deleting {len(ids)} datasets...")
            self._client.delete_datasets(ids=ids)
            logger.warning("RESET SYSTEM: Complete.")
        except Exception as e:
            logger.error(f"Failed to reset system: {e}")


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
