"""
PostgresStore - Long-Term Memory
================================
Cross-thread persistent memory using LangGraph PostgresStore.
Stores user preferences, memories, and learnings that persist
across all threads and conversations.
"""

import os
from typing import Optional, Dict, Any, List
from loguru import logger

# Try to import PostgresStore (requires langgraph-checkpoint-postgres)
try:
    from langgraph.store.postgres import PostgresStore
    HAS_POSTGRES_STORE = True
except ImportError:
    HAS_POSTGRES_STORE = False
    logger.warning("PostgresStore not available - install langgraph-checkpoint-postgres")

# Fallback to InMemoryStore
from langgraph.store.memory import InMemoryStore


class LongTermMemoryStore:
    """
    Long-term memory store for cross-thread data persistence.
    Falls back to InMemoryStore if PostgresStore is not available.
    """
    
    _instance: Optional["LongTermMemoryStore"] = None
    
    def __init__(self):
        self._store = None
        self._connected = False
        self._initialize()
    
    @classmethod
    def get_instance(cls) -> "LongTermMemoryStore":
        """Singleton pattern for store access."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _initialize(self):
        """Initialize the store with PostgreSQL or fallback to memory."""
        database_url = os.environ.get("DATABASE_URL")
        
        if database_url and HAS_POSTGRES_STORE:
            try:
                self._store = PostgresStore.from_conn_string(database_url)
                self._store.setup()
                self._connected = True
                logger.info("✅ PostgresStore initialized for long-term memory")
            except Exception as e:
                logger.warning(f"PostgresStore failed, using InMemoryStore: {e}")
                self._store = InMemoryStore()
                self._connected = False
        else:
            self._store = InMemoryStore()
            self._connected = False
            logger.warning("⚠️ Using InMemoryStore - long-term memory will not persist")
    
    @property
    def store(self):
        """Get the underlying store instance."""
        return self._store
    
    @property
    def is_persistent(self) -> bool:
        """Check if using persistent storage."""
        return self._connected
    
    # =========================================
    # MEMORY OPERATIONS
    # =========================================
    
    def remember(self, user_id: str, key: str, data: Dict[str, Any]) -> bool:
        """
        Store a memory for a user.
        
        Args:
            user_id: User identifier
            key: Memory key (unique within namespace)
            data: Data to store
        """
        try:
            namespace = ("memories", user_id)
            self._store.put(namespace, key, data)
            logger.debug(f"Stored memory: {user_id}/{key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False
    
    def recall(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search memories for a user.
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum results to return
        """
        try:
            namespace = ("memories", user_id)
            results = self._store.search(namespace, query=query, limit=limit)
            return [item.value for item in results]
        except Exception as e:
            logger.error(f"Failed to recall memories: {e}")
            return []
    
    def get_memory(self, user_id: str, key: str) -> Optional[Dict[str, Any]]:
        """Get a specific memory by key."""
        try:
            namespace = ("memories", user_id)
            item = self._store.get(namespace, key)
            return item.value if item else None
        except Exception as e:
            logger.error(f"Failed to get memory: {e}")
            return None
    
    def delete_memory(self, user_id: str, key: str) -> bool:
        """Delete a specific memory."""
        try:
            namespace = ("memories", user_id)
            self._store.delete(namespace, key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return False
    
    # =========================================
    # USER PREFERENCES
    # =========================================
    
    def set_preference(self, user_id: str, preference: str, value: Any) -> bool:
        """Store a user preference."""
        return self.remember(user_id, f"pref_{preference}", {"value": value})
    
    def get_preference(self, user_id: str, preference: str) -> Optional[Any]:
        """Get a user preference."""
        data = self.get_memory(user_id, f"pref_{preference}")
        return data.get("value") if data else None
    
    # =========================================
    # AGENT LEARNINGS
    # =========================================
    
    def store_learning(self, user_id: str, category: str, learning: str) -> bool:
        """Store an agent learning for a user."""
        import uuid
        key = f"learning_{category}_{uuid.uuid4().hex[:8]}"
        return self.remember(user_id, key, {
            "category": category,
            "learning": learning,
        })
    
    def get_learnings(self, user_id: str, category: str = None) -> List[str]:
        """Get all learnings for a user, optionally filtered by category."""
        results = self.recall(user_id, category or "learning")
        learnings = []
        for result in results:
            if "learning" in result:
                if category is None or result.get("category") == category:
                    learnings.append(result["learning"])
        return learnings


def get_long_term_memory() -> LongTermMemoryStore:
    """Get the long-term memory store instance."""
    return LongTermMemoryStore.get_instance()


# Export for easy import
__all__ = ["get_long_term_memory", "LongTermMemoryStore"]
