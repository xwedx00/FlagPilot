"""
Persistent Checkpointer - PostgreSQL Backend
=============================================
Production-ready checkpointer with PostgreSQL for state persistence.
NO MORE MemorySaver - state survives Docker restarts.
"""

import os
from typing import Optional
from loguru import logger

# Use sync checkpointer for simplicity with async wrapper
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver


class CheckpointerFactory:
    """
    Factory for creating checkpointers.
    Falls back to MemorySaver in development if PostgreSQL unavailable.
    """
    
    _instance: Optional[PostgresSaver] = None
    _fallback: Optional[MemorySaver] = None
    
    @classmethod
    def get_checkpointer(cls):
        """
        Get the production checkpointer (PostgreSQL) or fallback to memory.
        """
        # Try PostgreSQL first
        if cls._instance is not None:
            return cls._instance
        
        database_url = os.environ.get("DATABASE_URL")
        
        if database_url:
            try:
                # PostgresSaver.from_conn_string() returns a context manager
                # We need to enter the context to get the actual saver instance
                context_manager = PostgresSaver.from_conn_string(database_url)
                # Enter the context manager to get the actual PostgresSaver instance
                cls._instance = context_manager.__enter__()
                cls._instance.setup()  # Create tables if needed
                logger.info("✅ PostgresCheckpointer initialized - state will persist!")
                return cls._instance
            except Exception as e:
                logger.warning(f"PostgresCheckpointer failed, falling back to memory: {e}")
        
        # Fallback to memory saver
        if cls._fallback is None:
            cls._fallback = MemorySaver()
            logger.warning("⚠️ Using MemorySaver - state will be lost on restart!")
        
        return cls._fallback
    
    @classmethod
    def reset(cls):
        """Reset the checkpointer instance (for testing)."""
        cls._instance = None
        cls._fallback = None


def get_checkpointer():
    """Convenience function to get the checkpointer."""
    return CheckpointerFactory.get_checkpointer()


# Export for easy import
__all__ = ["get_checkpointer", "CheckpointerFactory"]
