"""
Qdrant Vector Store for FlagPilot v7.0
======================================
LangChain-integrated Qdrant client for document embeddings and RAG search.
"""

from typing import List, Optional, Dict, Any
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from config import settings


class QdrantStore:
    """Production Qdrant vector store for document embeddings"""
    
    _instance: Optional["QdrantStore"] = None
    _client: Optional[QdrantClient] = None
    _vector_store: Optional[QdrantVectorStore] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is not None:
            return
        self._initialize()
    
    def _initialize(self):
        """Initialize Qdrant client and embeddings"""
        try:
            # Connect to Qdrant
            self._client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
            logger.info(f"Connected to Qdrant at {settings.qdrant_url}")
            
            # Initialize embeddings via OpenRouter/OpenAI
            self._embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openrouter_api_key,
                openai_api_base=settings.openrouter_base_url,
            )
            
            # Ensure collection exists
            self._ensure_collection()
            
            # Create LangChain vector store
            self._vector_store = QdrantVectorStore(
                client=self._client,
                collection_name=settings.qdrant_collection,
                embedding=self._embeddings,
            )
            logger.info(f"Qdrant collection '{settings.qdrant_collection}' ready")
            
        except Exception as e:
            logger.error(f"Qdrant initialization failed: {e}")
            raise
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        collections = self._client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if settings.qdrant_collection not in collection_names:
            self._client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=qdrant_models.VectorParams(
                    size=1536,  # OpenAI embedding dimension
                    distance=qdrant_models.Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection: {settings.qdrant_collection}")
    
    @property
    def client(self) -> QdrantClient:
        """Get raw Qdrant client"""
        return self._client
    
    @property
    def vector_store(self) -> QdrantVectorStore:
        """Get LangChain vector store"""
        return self._vector_store
    
    async def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add documents to the vector store"""
        try:
            result = await self._vector_store.aadd_documents(
                documents=documents,
                ids=ids,
            )
            logger.info(f"Added {len(documents)} documents to Qdrant")
            return result
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """Search for similar documents"""
        try:
            results = await self._vector_store.asimilarity_search(
                query=query,
                k=k,
                filter=filter,
            )
            logger.debug(f"Found {len(results)} similar documents")
            return results
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[Document, float]]:
        """Search with relevance scores"""
        try:
            results = await self._vector_store.asimilarity_search_with_score(
                query=query,
                k=k,
                filter=filter,
            )
            return results
        except Exception as e:
            logger.error(f"Scored search failed: {e}")
            return []
    
    def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            self._client.delete_collection(settings.qdrant_collection)
            logger.warning(f"Deleted collection: {settings.qdrant_collection}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            info = self._client.get_collection(settings.qdrant_collection)
            return {
                "name": settings.qdrant_collection,
                "points_count": info.points_count,
                "indexed_vectors_count": getattr(info, 'indexed_vectors_count', info.points_count),
                "status": info.status.value,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}


# Singleton accessor
def get_qdrant_store() -> QdrantStore:
    """Get or create QdrantStore singleton"""
    return QdrantStore()
