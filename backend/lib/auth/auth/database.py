"""
Database Connection for Auth
============================
PostgreSQL connection for session validation.
Uses the same database as the frontend's BetterAuth.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import asyncpg
from loguru import logger


class DatabasePool:
    """
    Async PostgreSQL connection pool.
    Connects to the same database used by the frontend's BetterAuth.
    """
    
    _pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        """Get or create the connection pool."""
        if cls._pool is None:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise RuntimeError("DATABASE_URL environment variable not set")
            
            cls._pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=10,
                command_timeout=10,
            )
            logger.info("✅ Auth database pool initialized")
        return cls._pool
    
    @classmethod
    async def close(cls):
        """Close the connection pool."""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            logger.info("Auth database pool closed")


async def validate_session_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate a session token against the BetterAuth session table.
    
    Returns user data if valid, None if invalid or expired.
    
    The session table schema (from BetterAuth):
    - id: text (primary key)
    - token: text (unique)
    - expires_at: timestamp
    - user_id: text (references user.id)
    """
    try:
        pool = await DatabasePool.get_pool()
        
        # Query session with user join
        row = await pool.fetchrow(
            """
            SELECT 
                s.id as session_id,
                s.token,
                s.expires_at,
                s.user_id,
                u.id,
                u.name,
                u.email,
                u.image
            FROM session s
            JOIN "user" u ON s.user_id = u.id
            WHERE s.token = $1
            """,
            token
        )
        
        if not row:
            logger.debug(f"Session token not found")
            return None
        
        # Check expiration
        expires_at = row["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at < datetime.now(timezone.utc):
            logger.debug(f"Session expired for user {row['user_id']}")
            return None
        
        return {
            "user_id": row["user_id"],
            "session_id": row["session_id"],
            "name": row["name"],
            "email": row["email"],
            "image": row["image"],
        }
        
    except asyncpg.PostgresError as e:
        logger.error(f"Database error validating session: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error validating session: {e}")
        return None


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user details by ID.
    
    Returns user data or None if not found.
    """
    try:
        pool = await DatabasePool.get_pool()
        
        row = await pool.fetchrow(
            """
            SELECT id, name, email, image, email_verified, created_at, updated_at
            FROM "user"
            WHERE id = $1
            """,
            user_id
        )
        
        if not row:
            return None
        
        return dict(row)
        
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        return None
