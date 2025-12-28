"""
Health Check Router v7.0
========================
Service health checks for Qdrant, Elasticsearch, MinIO, Redis, PostgreSQL
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
from loguru import logger

router = APIRouter(tags=["Health"])


class ServiceStatus(BaseModel):
    status: str
    message: str


@router.get("/health/services")
async def service_health() -> Dict[str, ServiceStatus]:
    """Check status of all services"""
    services = {}
    
    # Redis
    try:
        from lib.redis_client import get_redis
        redis = get_redis()
        if redis:
            await redis.ping()
            services["redis"] = ServiceStatus(status="healthy", message="Connected")
        else:
            services["redis"] = ServiceStatus(status="unavailable", message="Not configured")
    except Exception as e:
        services["redis"] = ServiceStatus(status="unhealthy", message=str(e))
    
    # Qdrant (Vector DB)
    try:
        from qdrant_client import QdrantClient
        from config import settings
        
        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        collections = client.get_collections()
        services["qdrant"] = ServiceStatus(
            status="healthy",
            message=f"Connected, {len(collections.collections)} collections"
        )
    except Exception as e:
        services["qdrant"] = ServiceStatus(status="unhealthy", message=str(e))
    
    # Elasticsearch
    try:
        from elasticsearch import Elasticsearch
        from config import settings
        
        es = Elasticsearch([settings.es_url])
        if es.ping():
            info = es.info()
            services["elasticsearch"] = ServiceStatus(
                status="healthy",
                message=f"Connected, version {info['version']['number']}"
            )
        else:
            services["elasticsearch"] = ServiceStatus(status="unhealthy", message="Ping failed")
    except Exception as e:
        services["elasticsearch"] = ServiceStatus(status="unhealthy", message=str(e))
    
    # MinIO
    try:
        from minio import Minio
        from config import settings
        
        client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        buckets = list(client.list_buckets())
        services["minio"] = ServiceStatus(
            status="healthy",
            message=f"Connected, {len(buckets)} buckets"
        )
    except Exception as e:
        services["minio"] = ServiceStatus(status="unhealthy", message=str(e))
    
    # PostgreSQL
    try:
        import asyncpg
        from config import settings
        
        if settings.database_url:
            conn = await asyncpg.connect(settings.database_url)
            version = await conn.fetchval("SELECT version()")
            await conn.close()
            services["postgresql"] = ServiceStatus(
                status="healthy",
                message="Connected"
            )
        else:
            services["postgresql"] = ServiceStatus(status="unavailable", message="Not configured")
    except Exception as e:
        services["postgresql"] = ServiceStatus(status="unhealthy", message=str(e))
    
    return services


@router.get("/health/rag")
async def rag_health() -> Dict:
    """Check RAG pipeline status (Qdrant + MinIO)"""
    try:
        from lib.vectorstore import get_qdrant_store
        from lib.storage import get_minio_storage
        
        qdrant = get_qdrant_store()
        minio = get_minio_storage()
        
        collection_info = qdrant.get_collection_info()
        files = minio.list_files()
        
        return {
            "status": "healthy",
            "qdrant": collection_info,
            "minio_files": len(files),
        }
    except Exception as e:
        logger.error(f"RAG health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}
