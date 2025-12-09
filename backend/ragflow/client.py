"""
RAGFlow Client for FlagPilot
=============================
Integrates RAGFlow for document understanding and vector search.
Matches official RAGFlow Python SDK.

Two namespaces:
- Personal Vault: User-specific documents (One dataset per user: 'user_<id>')
- Global Wisdom: Shared successful workflows (Dataset: 'global_wisdom')
"""

import os
import time
from typing import Optional, List, Dict, Any
from loguru import logger

# Global instance
_ragflow_client: Optional["RAGFlowClient"] = None


class RAGFlowClient:
    """
    RAGFlow SDK wrapper for FlagPilot.
    
    Provides:
    - Personal document storage (Dataset Management)
    - Global wisdom store
    - Retrieval (Chunks) for Agent Context
    """
    
    def __init__(self):
        self.api_key = os.getenv("RAGFLOW_API_KEY", "")
        self.base_url = os.getenv("RAGFLOW_URL", "http://ragflow:9380")
        self._client = None
        self._connected = False
        
        self._connect()
    
    def _connect(self):
        """Initialize RAGFlow SDK connection"""
        if not self.api_key:
            logger.warning("RAGFLOW_API_KEY not set - RAGFlow disabled")
            return
        
        try:
            from ragflow_sdk import RAGFlow
            self._client = RAGFlow(
                api_key=self.api_key,
                base_url=self.base_url
            )
            # Verify connection by listing datasets (lightweight check)
            self._client.list_datasets(page=1, page_size=1)
            self._connected = True
            logger.info(f"✅ RAGFlow connected at {self.base_url}")
        
        except ImportError:
            logger.error("ragflow-sdk not installed - run: pip install ragflow-sdk")
            raise
        except Exception as e:
            logger.error(f"❌ RAGFlow connection failed (Key provided but unreachable): {e}")
            # Fail Fast: If key is provided, we expect it to work.
            raise ConnectionError(f"RAGFlow unreachable: {e}")
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    # =========================================================================
    # Dataset Management Helpers
    # =========================================================================
    
    def _get_or_create_dataset(self, name: str, description: str = "") -> Any:
        """Helper to get or create a dataset by name"""
        if not self._client:
            raise ConnectionError("RAGFlow client not connected")
            
    def _get_or_create_dataset(self, name: str, description: str = "") -> Any:
        """Helper to get or create a dataset by name"""
        if not self._client:
            raise ConnectionError("RAGFlow client not connected")
            
        # Strategy: Try to find it first (cleaner logs), then create if missing.
        target = None
        try:
            # 1. Try to find existing
            datasets = self._client.list_datasets(name=name, page=1, page_size=10)
            target = next((d for d in datasets if d.name == name), None)
        except Exception as e:
            logger.warning(f"List dataset '{name}' failed (will create): {e}")

        if target:
            return target

        try:
            # 2. Create if not found
            dataset = self._client.create_dataset(
                name=name,
                description=description,
                permission="me"
            )
            logger.info(f"Created RAGFlow dataset: {name}")
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to create dataset {name}: {e}")
            raise RuntimeError(f"Failed to get/create dataset {name}") from e

    # =========================================================================
    # Personal Vault (User-specific RAG)
    # =========================================================================
    
    def get_user_dataset_name(self, user_id: str) -> str:
        """Generate safe dataset name for user"""
        # Dataset names must be BMP only, max 128 chars. 
        # We use a prefix and potentially truncated ID.
        safe_id = user_id.replace("-", "_")
        return f"pv_{safe_id}"[:64] # pv = personal vault
    
    async def add_user_document(
        self,
        user_id: str,
        content: bytes,
        filename: str,
        doc_type: str = "document"
    ) -> bool:
        """Add a document to user's personal vault"""
        if not self._client:
            raise ConnectionError("RAGFlow client not connected")
            
        try:
            name = self.get_user_dataset_name(user_id)
            dataset = self._get_or_create_dataset(name, f"Personal Vault for {user_id}")
            
            if not dataset:
                # Should not happen given _get_or_create raises, but for type safety
                raise RuntimeError(f"Could not retrieve dataset {name}")
            
            # Upload document
            documents = [{
                "display_name": filename,
                "blob": content
            }]
            
            dataset.upload_documents(documents)
            
            # Trigger parsing (Asynchronous)
            time.sleep(1) # Brief wait for consistency
            
            docs = dataset.list_documents(keywords=filename, page=1, page_size=5)
            doc_ids = [d.id for d in docs if d.name == filename]
            
            if doc_ids:
                try:
                    dataset.async_parse_documents(doc_ids)
                    logger.info(f"Triggered parsing for {len(doc_ids)} docs in {name}")
                except Exception as parse_err:
                    # RAGFlow might throw "Can't stop parsing..." if already running/done.
                    # We treat this as success (it's being processed).
                    logger.warning(f"Parse trigger warning for {name}: {parse_err}")
            else:
                logger.warning(f"Uploaded {filename} but could not find ID to trigger parse.")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document to {user_id}: {e}")
            raise RuntimeError(f"Document upload failed: {e}") from e
    
    async def search_user_context(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Search user's personal vault"""
        if not self._client:
            # If not connected, we can't search. Raising ensures agent knows it failed.
            raise ConnectionError("RAGFlow client not connected")
            
        try:
            name = self.get_user_dataset_name(user_id)
            # We need the dataset ID for retrieval
            dataset = self._get_or_create_dataset(name)
            
            # Use top-level retrieve method
            logger.debug(f"Searching user context {name} q='{query[:50]}...' thresh={similarity_threshold}")
            chunks = self._client.retrieve(
                question=query,
                dataset_ids=[dataset.id],
                top_k=limit,
                similarity_threshold=similarity_threshold
            )
            
            logger.info(f"Retrieved {len(chunks)} chunks for {user_id}")
            
            results = []
            for chunk in chunks:
                results.append({
                    "content": getattr(chunk, "content_with_weight", getattr(chunk, "content", "")),
                    "content_with_weight": getattr(chunk, "content_with_weight", getattr(chunk, "content", "")), # Map for frontend/test consistency
                    "similarity": getattr(chunk, "similarity", 0.0),
                    "document_name": getattr(chunk, "document_name", "unknown"),
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Search failed for {user_id}: {e}")
            # For search, if it fails, maybe user has no docs or system down.
            # But "system down" should raise. 
            # If dataset creation failed (e.g. valid user but broken RAG), we raised in _get_or_create.
            # So here any catch is likely a retrieval error.
            raise RuntimeError(f"RAG Search failed: {e}") from e

    # =========================================================================
    # Global Wisdom (Shared Knowledge)
    # =========================================================================
    
    def _get_global_dataset(self) -> Any:
        return self._get_or_create_dataset("global_wisdom", "Shared successful agent workflows")

    async def add_successful_workflow(
        self,
        summary: str,
        workflow_type: str,
        agents_used: List[str],
        rating: int = 5
    ) -> bool:
        """Add workflow to Global Wisdom"""
        if not self._client:
            return False
            
        try:
            dataset = self._get_global_dataset()
            if not dataset:
                return False
            
            # Create a structured text representation
            content = f"""
            TYPE: {workflow_type}
            RATING: {rating}/5
            AGENTS: {', '.join(agents_used)}
            SUMMARY: {summary}
            """
            
            filename = f"workflow_{int(time.time())}_{workflow_type}.txt"
            
            dataset.upload_documents([{
                "display_name": filename,
                "blob": content.encode('utf-8')
            }])
            
            # Auto-parse
            time.sleep(1)
            docs = dataset.list_documents(keywords=filename, page=1, page_size=1)
            if docs:
                dataset.async_parse_documents([docs[0].id])
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to add global wisdom: {e}")
            return False

    async def get_workflow_suggestions(
        self,
        query: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get suggestions from Global Wisdom"""
        if not self._client:
            return []
            
        try:
            dataset = self._get_global_dataset()
            if not dataset:
                return []
            
            chunks = self._client.retrieve(
                question=query,
                dataset_ids=[dataset.id],
                top_k=limit,
                similarity_threshold=0.1
            )
            
            return [{"content": c.content_with_weight, "similarity": c.similarity} for c in chunks]
            
        except Exception as e:
            logger.error(f"Global wisdom query failed: {e}")
            return []

    # =========================================================================
    # Combined Context for Agents
    # =========================================================================
    
    async def get_agent_context(
        self,
        user_id: str,
        query: str
    ) -> str:
        """
        Aggregates context from Personal Vault and Global Wisdom 
        to assist MetaGPT agents.
        """
        context_parts = []
        
        # 1. Personal Context
        user_results = await self.search_user_context(user_id, query, limit=10, similarity_threshold=0.1)
        if user_results:
            context_parts.append("## Personal Knowledge (User Files)")
            for i, r in enumerate(user_results, 1):
                context_parts.append(f"{i}. {r['content']} (Source: {r['document_name']})")
        else:
            logger.warning(f"No personal context found for {user_id} with query '{query[:30]}...'")
        
        # 2. Global Wisdom
        global_results = await self.get_workflow_suggestions(query, limit=2)
        if global_results:
            context_parts.append("\n## Global Patterns (Successful Workflows)")
            for i, r in enumerate(global_results, 1):
                context_parts.append(f"{i}. {r['content']}")
                
        if not context_parts:
            return ""
            
        full_context = "\n".join(context_parts)
        logger.info(f"Generated Context ({len(full_context)} chars) for {user_id}")
        return full_context


def get_ragflow_client() -> RAGFlowClient:
    """Get singleton RAGFlow client"""
    global _ragflow_client
    if _ragflow_client is None:
        _ragflow_client = RAGFlowClient()
    return _ragflow_client
