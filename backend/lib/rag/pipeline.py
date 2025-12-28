"""
RAG Pipeline for FlagPilot v7.0
===============================
Document ingestion, chunking, embedding, and retrieval using LangChain + Qdrant.
"""

from typing import List, Optional, Dict, Any, BinaryIO
from io import BytesIO
import uuid
from loguru import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from lib.vectorstore import get_qdrant_store
from lib.storage import get_minio_storage
from config import settings


class RAGPipeline:
    """
    Production RAG Pipeline:
    1. Upload file to MinIO
    2. Extract text content
    3. Chunk with RecursiveCharacterTextSplitter
    4. Embed and store in Qdrant
    5. Retrieve relevant chunks for queries
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.qdrant = get_qdrant_store()
        self.minio = get_minio_storage()
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
    
    async def ingest_text(
        self,
        text: str,
        source: str = "user_input",
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ingest plain text into the RAG system.
        
        Args:
            text: The text content to ingest
            source: Source identifier
            metadata: Additional metadata
            user_id: User who uploaded
            
        Returns:
            Dict with chunk_count and doc_ids
        """
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create documents with metadata
            base_metadata = {
                "source": source,
                "user_id": user_id or "anonymous",
                "type": "text",
                **(metadata or {}),
            }
            
            documents = [
                Document(
                    page_content=chunk,
                    metadata={
                        **base_metadata,
                        "chunk_index": i,
                        "chunk_id": f"{source}_{i}",
                    },
                )
                for i, chunk in enumerate(chunks)
            ]
            
            # Add to Qdrant
            doc_ids = await self.qdrant.add_documents(documents)
            
            logger.info(f"Ingested {len(chunks)} chunks from '{source}'")
            
            return {
                "success": True,
                "chunk_count": len(chunks),
                "doc_ids": doc_ids,
                "source": source,
            }
            
        except Exception as e:
            logger.error(f"Text ingestion failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def ingest_file(
        self,
        file_data: BinaryIO,
        file_name: str,
        content_type: str = "text/plain",
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Ingest a file into the RAG system.
        
        1. Upload to MinIO for storage
        2. Extract text (basic - extend for PDF/DOCX)
        3. Chunk and embed into Qdrant
        """
        try:
            # Upload to MinIO first
            upload_result = self.minio.upload_file(
                file_data=file_data,
                file_name=file_name,
                content_type=content_type,
                user_id=user_id,
                metadata=metadata,
            )
            
            # Reset file pointer and read content
            file_data.seek(0)
            content = file_data.read()
            
            # Decode text (basic - extend for binary formats)
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                # For binary files, note: extend this for PDF parsing
                text = content.decode("latin-1")
            
            # Ingest the text
            ingest_result = await self.ingest_text(
                text=text,
                source=upload_result["object_name"],
                user_id=user_id,
                metadata={
                    "original_name": file_name,
                    "content_type": content_type,
                    "minio_object": upload_result["object_name"],
                    **(metadata or {}),
                },
            )
            
            return {
                **ingest_result,
                "file": upload_result,
            }
            
        except Exception as e:
            logger.error(f"File ingestion failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def retrieve(
        self,
        query: str,
        k: int = 5,
        user_id: Optional[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            k: Number of results
            user_id: Filter by user
            filter_metadata: Additional filters
            
        Returns:
            List of relevant documents
        """
        # Build filter
        filter_dict = filter_metadata or {}
        if user_id:
            filter_dict["user_id"] = user_id
        
        return await self.qdrant.similarity_search(
            query=query,
            k=k,
            filter=filter_dict if filter_dict else None,
        )
    
    async def retrieve_with_scores(
        self,
        query: str,
        k: int = 5,
        min_score: float = 0.0,
    ) -> List[tuple[Document, float]]:
        """Retrieve with relevance scores, optionally filtering by minimum score"""
        results = await self.qdrant.similarity_search_with_score(
            query=query,
            k=k,
        )
        
        # Filter by minimum score
        if min_score > 0:
            results = [(doc, score) for doc, score in results if score >= min_score]
        
        return results
    
    def get_context_for_query(
        self,
        documents: List[Document],
        max_tokens: int = 4000,
    ) -> str:
        """Format retrieved documents as context string for LLM"""
        context_parts = []
        current_length = 0
        
        for doc in documents:
            content = doc.page_content
            source = doc.metadata.get("source", "unknown")
            
            # Rough token estimate (4 chars per token)
            estimated_tokens = len(content) // 4
            
            if current_length + estimated_tokens > max_tokens:
                break
            
            context_parts.append(f"[Source: {source}]\n{content}")
            current_length += estimated_tokens
        
        return "\n\n---\n\n".join(context_parts)


# Factory function
def get_rag_pipeline(
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> RAGPipeline:
    """Get a RAG pipeline instance"""
    return RAGPipeline(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
