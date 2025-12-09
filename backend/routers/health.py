"""
Health Check Router
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from datetime import datetime

router = APIRouter(tags=["Health"])


class ServiceStatus(BaseModel):
    status: str
    message: str


@router.get("/health/services")
async def service_health() -> Dict[str, ServiceStatus]:
    """Check status of all services"""
    services = {}
    
    # PostgreSQL
    try:
        from lib.database import get_db
        db = get_db()
        services["postgres"] = ServiceStatus(status="healthy", message="Connected")
    except Exception as e:
        services["postgres"] = ServiceStatus(status="unhealthy", message=str(e))
    
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
    
    # Qdrant
    try:
        from rag import get_vector_store
        vs = get_vector_store()
        if vs.client:
            services["qdrant"] = ServiceStatus(status="healthy", message="Connected")
        else:
            services["qdrant"] = ServiceStatus(status="unavailable", message="Not connected")
    except Exception as e:
        services["qdrant"] = ServiceStatus(status="unhealthy", message=str(e))
    
    return services
