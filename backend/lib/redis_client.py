"""
Redis Client for Caching
"""

import os
from typing import Optional
from loguru import logger

_redis_client = None


async def init_redis():
    """Initialize Redis connection"""
    global _redis_client
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    try:
        import redis.asyncio as redis
        _redis_client = redis.from_url(redis_url, decode_responses=True)
        await _redis_client.ping()
        logger.info("Redis connected")
    except ImportError:
        logger.warning("redis package not installed - caching disabled")
        _redis_client = None
    except Exception as e:
        logger.warning(f"Redis not available: {e}")
        _redis_client = None


async def close_redis():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        logger.info("Redis connection closed")


def get_redis():
    """Get Redis client"""
    return _redis_client


async def cache_get(key: str) -> Optional[str]:
    """Get value from cache"""
    if _redis_client:
        return await _redis_client.get(key)
    return None


async def cache_set(key: str, value: str, expire: int = 3600):
    """Set value in cache"""
    if _redis_client:
        await _redis_client.set(key, value, ex=expire)
