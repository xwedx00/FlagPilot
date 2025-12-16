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
    
    # RAGFlow
    try:
        import httpx
        from config import settings
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.RAGFLOW_URL}/v1/health", timeout=5.0)
            if resp.status_code == 200:
                services["ragflow"] = ServiceStatus(status="healthy", message="Connected")
            else:
                services["ragflow"] = ServiceStatus(status="unhealthy", message=f"Status {resp.status_code}")
    except Exception as e:
        services["ragflow"] = ServiceStatus(status="unhealthy", message=str(e))
    
    return services
