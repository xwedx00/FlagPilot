"""
Rate Limiter - Tier-Based Rate Limiting
========================================
Real rate limiting with tier-based limits.
NO MOCKS. Production-ready implementation.
"""

from lib.redis_client import get_redis
from lib.auth.database import DatabasePool
from fastapi import HTTPException
from loguru import logger
from typing import Optional


# Tier-based rate limits (requests per hour)
TIER_RATE_LIMITS = {
    "free": {"requests_per_hour": 20, "burst_limit": 5},
    "starter": {"requests_per_hour": 100, "burst_limit": 15},
    "professional": {"requests_per_hour": 500, "burst_limit": 50},
    "enterprise": {"requests_per_hour": 2000, "burst_limit": 100},
}


class RateLimiter:
    """
    Tier-based rate limiter with Redis backend.
    - Different limits per subscription tier
    - Burst protection
    - Real-time quota tracking
    """
    
    @staticmethod
    async def get_user_tier(user_id: str) -> str:
        """Get user's subscription tier from database."""
        if user_id == "anonymous":
            return "free"
        
        try:
            pool = await DatabasePool.get_pool()
            row = await pool.fetchrow(
                'SELECT subscription_tier FROM "user" WHERE id = $1',
                user_id
            )
            return row["subscription_tier"] if row else "free"
        except Exception as e:
            logger.error(f"Error getting user tier: {e}")
            return "free"
    
    @staticmethod
    async def check_rate_limit(
        user_id: str, 
        limit: Optional[int] = None, 
        window: int = 3600
    ) -> dict:
        """
        Check rate limit for user using Redis.
        Uses tier-based limits if user_id is authenticated.
        
        Returns dict with:
        - allowed: bool
        - remaining: int
        - limit: int
        - reset_in: int (seconds)
        """
        redis = get_redis()
        if not redis:
            # Fail open if Redis is down
            return {"allowed": True, "remaining": 999, "limit": 999}
        
        try:
            # Get tier-based limit
            if limit is None:
                tier = await RateLimiter.get_user_tier(user_id)
                tier_config = TIER_RATE_LIMITS.get(tier, TIER_RATE_LIMITS["free"])
                limit = tier_config["requests_per_hour"]
            
            key = f"rate_limit:{user_id}:hourly"
            current = await redis.incr(key)
            
            if current == 1:
                await redis.expire(key, window)
            
            ttl = await redis.ttl(key)
            remaining = max(0, limit - current)
            
            if current > limit:
                logger.warning(f"Rate limit exceeded for {user_id}: {current}/{limit}")
                raise HTTPException(
                    status_code=429, 
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": limit,
                        "reset_in_seconds": ttl,
                        "upgrade_url": "/pricing"
                    }
                )
            
            return {
                "allowed": True,
                "remaining": remaining,
                "limit": limit,
                "reset_in": ttl,
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return {"allowed": True, "remaining": 999, "limit": 999}
    
    @staticmethod
    async def check_burst_limit(user_id: str) -> bool:
        """
        Check burst limit (requests per minute).
        Prevents abuse from rapid-fire requests.
        """
        redis = get_redis()
        if not redis:
            return True
        
        try:
            tier = await RateLimiter.get_user_tier(user_id)
            tier_config = TIER_RATE_LIMITS.get(tier, TIER_RATE_LIMITS["free"])
            burst_limit = tier_config["burst_limit"]
            
            key = f"rate_limit:{user_id}:burst"
            current = await redis.incr(key)
            
            if current == 1:
                await redis.expire(key, 60)  # 1 minute window
            
            if current > burst_limit:
                logger.warning(f"Burst limit exceeded for {user_id}: {current}/{burst_limit}")
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please slow down."
                )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Burst limit check failed: {e}")
            return True
    
    @staticmethod
    async def get_usage_stats(user_id: str) -> dict:
        """Get current usage stats for a user."""
        redis = get_redis()
        if not redis:
            return {"hourly_used": 0, "daily_used": 0}
        
        try:
            hourly_key = f"rate_limit:{user_id}:hourly"
            daily_key = f"rate_limit:{user_id}:daily"
            
            hourly = await redis.get(hourly_key)
            daily = await redis.get(daily_key)
            
            tier = await RateLimiter.get_user_tier(user_id)
            tier_config = TIER_RATE_LIMITS.get(tier, TIER_RATE_LIMITS["free"])
            
            return {
                "tier": tier,
                "hourly_limit": tier_config["requests_per_hour"],
                "hourly_used": int(hourly) if hourly else 0,
                "burst_limit": tier_config["burst_limit"],
            }
            
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {"hourly_used": 0}


# Singleton instance
rate_limiter = RateLimiter()
