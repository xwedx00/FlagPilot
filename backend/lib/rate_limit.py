
from lib.redis_client import get_redis
from fastapi import HTTPException
from loguru import logger

class RateLimiter:
    @staticmethod
    async def check_rate_limit(user_id: str, limit: int = 100, window: int = 3600):
        """
        Check rate limit for user using Redis.
        Default: 100 requests per hour (Generous for now).
        Raises 429 if exceeded.
        """
        if user_id == "anonymous":
            return True

        redis = get_redis()
        if not redis:
             # Fail open if Redis is down
            return True
        
        try:    
            key = f"rate_limit:{user_id}"
            current = await redis.incr(key)
            
            if current == 1:
                await redis.expire(key, window)
                
            if current > limit:
                logger.warning(f"Rate limit exceeded for {user_id}: {current}/{limit}")
                raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Try again in {window//60} mins.")
                
            return True
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Rate limit check failed: {e}")
            return True
