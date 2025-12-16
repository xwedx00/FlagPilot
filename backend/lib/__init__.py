"""
FlagPilot Backend Library - Simplified
"""

from .redis_client import get_redis, init_redis, close_redis
from .config import get_settings

__all__ = [
    "get_redis",
    "init_redis",
    "close_redis",
    "get_settings",
]
