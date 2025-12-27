"""
Persistent Checkpointer - PostgreSQL Backend (Async)
======================================================
Production-ready checkpointer with PostgreSQL for state persistence.
Uses AsyncPostgresSaver for proper async streaming support with CopilotKit.
"""

import os
from typing import Optional
from loguru import logger

# Use async checkpointer for streaming compatibility
try:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    HAS_ASYNC_PG = True
except ImportError:
    HAS_ASYNC_PG = False
    logger.warning("AsyncPostgresSaver not available")

from langgraph.checkpoint.memory import MemorySaver


class CheckpointerFactory:
    """
    Factory for creating checkpointers.
    Uses AsyncPostgresSaver for async streaming operations.
    Falls back to MemorySaver in development if PostgreSQL unavailable.
    """
    
    _instance = None
    _fallback: Optional[MemorySaver] = None
    _context_manager = None
    
    @classmethod
    def get_checkpointer(cls):
        """
        Get the production checkpointer (PostgreSQL async) or fallback to memory.
        """
        # Return existing instance
        if cls._instance is not None:
            return cls._instance
        
        database_url = os.environ.get("DATABASE_URL")
        
        if database_url and HAS_ASYNC_PG:
            try:
                # AsyncPostgresSaver.from_conn_string() returns a context manager
                # We need to enter it to get the actual saver instance
                cls._context_manager = AsyncPostgresSaver.from_conn_string(database_url)
                cls._instance = cls._context_manager.__enter__()
                # Run setup synchronously (tables creation is sync-safe)
                cls._instance.setup()
                logger.info("✅ AsyncPostgresSaver initialized - async streaming + persistence!")
                return cls._instance
            except Exception as e:
                logger.warning(f"AsyncPostgresSaver failed, falling back to memory: {e}")
        
        # Fallback to memory saver
        if cls._fallback is None:
            cls._fallback = MemorySaver()
            if not database_url:
                logger.warning("⚠️ Using MemorySaver - DATABASE_URL not set!")
            else:
                logger.warning("⚠️ Using MemorySaver - state will be lost on restart!")
        
        return cls._fallback
    
    @classmethod
    def reset(cls):
        """Reset the checkpointer instance (for testing)."""
        if cls._context_manager:
            try:
                cls._context_manager.__exit__(None, None, None)
            except:
                pass
        cls._instance = None
        cls._fallback = None
        cls._context_manager = None


def get_checkpointer():
    """Convenience function to get the checkpointer."""
    return CheckpointerFactory.get_checkpointer()


# Export for easy import
__all__ = ["get_checkpointer", "CheckpointerFactory"]

