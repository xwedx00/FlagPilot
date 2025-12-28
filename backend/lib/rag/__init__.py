"""
RAG Module for FlagPilot v7.0
=============================
LangChain-based RAG pipeline with Qdrant + MinIO.
"""

from lib.rag.pipeline import RAGPipeline, get_rag_pipeline

__all__ = ["RAGPipeline", "get_rag_pipeline"]
