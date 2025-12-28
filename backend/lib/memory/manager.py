"""
Memory Manager - Elasticsearch-based Memory System
===================================================
Triple-Tiered Memory for FlagPilot:
1. Dynamic User Profiles - Personal learnings
2. Chat History - Conversation logs per user
3. Experience Gallery (Global Wisdom) - Anonymized shared learnings
"""

from elasticsearch import Elasticsearch
from loguru import logger
from config import settings
from typing import Optional, List, Dict, Any
import datetime
import uuid


class MemoryManager:
    """
    Production-ready Memory Manager using Elasticsearch.
    Manages user profiles, chat history, and global wisdom.
    """
    
    # Index names
    PROFILE_INDEX = "flagpilot_user_profiles"
    CHAT_INDEX = "flagpilot_chat_history"
    GALLERY_INDEX = "flagpilot_experience_gallery"
    WISDOM_INDEX = "flagpilot_global_wisdom"
    
    def __init__(self, es_host: str = None, es_port: int = None):
        """
        Initialize the Memory Manager with Elasticsearch connection.
        Falls back gracefully if ES is unavailable.
        """
        self.es_host = es_host or settings.es_host
        self.es_port = es_port or settings.es_port
        self.es_url = f"http://{self.es_host}:{self.es_port}"
        self.connected = False
        self.client = None
        
        try:
            self.client = Elasticsearch(
                self.es_url,
                verify_certs=False,
                request_timeout=10,
                retry_on_timeout=True,
                max_retries=3
            )
            # Test connection
            if self.client.ping():
                self.connected = True
                logger.info(f"MemoryManager connected to ES at {self.es_url}")
                self._ensure_indices()
            else:
                logger.warning(f"MemoryManager: ES ping failed at {self.es_url}")
        except Exception as e:
            logger.warning(f"MemoryManager: ES connection failed: {e}")
            self.connected = False
    
    def _ensure_indices(self):
        """Create indices if they don't exist."""
        if not self.connected:
            return
            
        indices = {
            self.PROFILE_INDEX: {
                "properties": {
                    "user_id": {"type": "keyword"},
                    "summary": {"type": "text"},
                    "preferences": {"type": "object", "enabled": False},
                    "learning_style": {"type": "keyword"},
                    "risk_tolerance": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "last_updated": {"type": "date"}
                }
            },
            self.CHAT_INDEX: {
                "properties": {
                    "user_id": {"type": "keyword"},
                    "session_id": {"type": "keyword"},
                    "role": {"type": "keyword"},  # user/assistant
                    "content": {"type": "text"},
                    "agent_id": {"type": "keyword"},
                    "metadata": {"type": "object", "enabled": False},
                    "timestamp": {"type": "date"}
                }
            },
            self.GALLERY_INDEX: {
                "properties": {
                    "user_id": {"type": "keyword"},
                    "task_type": {"type": "keyword"},
                    "input_query": {"type": "text"},
                    "outcome": {"type": "text"},
                    "lesson": {"type": "text"},
                    "feedback_score": {"type": "integer"},
                    "is_public": {"type": "boolean"},
                    "created_at": {"type": "date"}
                }
            },
            self.WISDOM_INDEX: {
                "properties": {
                    "category": {"type": "keyword"},  # contract, scam, negotiation, etc.
                    "insight": {"type": "text"},
                    "source_count": {"type": "integer"},  # How many users contributed
                    "confidence_score": {"type": "float"},
                    "tags": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "last_updated": {"type": "date"}
                }
            }
        }
        
        try:
            for index_name, mapping in indices.items():
                if not self.client.indices.exists(index=index_name):
                    self.client.indices.create(
                        index=index_name,
                        body={"mappings": mapping}
                    )
                    logger.info(f"Created index: {index_name}")
        except Exception as e:
            logger.error(f"Failed to ensure indices: {e}")
    
    # ==========================================
    # User Profile Methods
    # ==========================================
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Retrieve the full user profile."""
        if not self.connected:
            return {"user_id": user_id, "summary": "", "preferences": {}}
            
        try:
            res = self.client.get(index=self.PROFILE_INDEX, id=user_id, ignore=[404])
            if res.get("found"):
                return res["_source"]
            return {"user_id": user_id, "summary": "", "preferences": {}}
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {"user_id": user_id, "summary": "", "preferences": {}}
    
    async def get_current_user_profile(self, user_id: str) -> str:
        """Retrieve just the profile summary string (backward compatible)."""
        profile = await self.get_user_profile(user_id)
        return profile.get("summary", "")
    
    async def update_user_profile(
        self,
        user_id: str,
        summary: str = None,
        preferences: Dict = None,
        **kwargs
    ):
        """Update user profile with partial updates."""
        if not self.connected:
            logger.warning("ES not connected, skipping profile update")
            return False
            
        try:
            now = datetime.datetime.utcnow().isoformat()
            
            # Get existing profile
            existing = await self.get_user_profile(user_id)
            
            # Merge updates
            body = {
                "user_id": user_id,
                "summary": summary if summary is not None else existing.get("summary", ""),
                "preferences": preferences if preferences is not None else existing.get("preferences", {}),
                "last_updated": now,
                **kwargs
            }
            
            if not existing.get("created_at"):
                body["created_at"] = now
            else:
                body["created_at"] = existing["created_at"]
            
            self.client.index(index=self.PROFILE_INDEX, id=user_id, body=body)
            logger.info(f"Updated profile for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
    
    # ==========================================
    # Chat History Methods
    # ==========================================
    
    async def save_chat(
        self,
        user_id: str,
        role: str,
        content: str,
        session_id: str = None,
        agent_id: str = None,
        metadata: Dict = None
    ) -> str:
        """Save a chat message to history."""
        if not self.connected:
            return ""
            
        try:
            chat_id = str(uuid.uuid4())
            body = {
                "user_id": user_id,
                "session_id": session_id or str(uuid.uuid4()),
                "role": role,
                "content": content,
                "agent_id": agent_id,
                "metadata": metadata or {},
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            
            self.client.index(index=self.CHAT_INDEX, id=chat_id, body=body)
            logger.debug(f"Saved chat message for user {user_id}")
            return chat_id
        except Exception as e:
            logger.error(f"Error saving chat: {e}")
            return ""
    
    async def get_chat_history(
        self,
        user_id: str,
        session_id: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get chat history for a user, optionally filtered by session."""
        if not self.connected:
            return []
            
        try:
            query = {
                "bool": {
                    "must": [{"term": {"user_id": user_id}}]
                }
            }
            
            if session_id:
                query["bool"]["must"].append({"term": {"session_id": session_id}})
            
            res = self.client.search(
                index=self.CHAT_INDEX,
                body={
                    "size": limit,
                    "query": query,
                    "sort": [{"timestamp": "desc"}]
                }
            )
            
            messages = [hit["_source"] for hit in res.get("hits", {}).get("hits", [])]
            return list(reversed(messages))  # Chronological order
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []
    
    async def get_recent_sessions(self, user_id: str, limit: int = 10) -> List[str]:
        """Get recent session IDs for a user."""
        if not self.connected:
            return []
            
        try:
            res = self.client.search(
                index=self.CHAT_INDEX,
                body={
                    "size": 0,
                    "query": {"term": {"user_id": user_id}},
                    "aggs": {
                        "sessions": {
                            "terms": {
                                "field": "session_id",
                                "size": limit,
                                "order": {"latest": "desc"}
                            },
                            "aggs": {
                                "latest": {"max": {"field": "timestamp"}}
                            }
                        }
                    }
                }
            )
            
            buckets = res.get("aggregations", {}).get("sessions", {}).get("buckets", [])
            return [b["key"] for b in buckets]
        except Exception as e:
            logger.error(f"Error getting sessions: {e}")
            return []
    
    # ==========================================
    # Experience Gallery Methods
    # ==========================================
    
    async def save_experience(
        self,
        user_id: str,
        task: str,
        outcome: str,
        lesson: str,
        score: int = 1,
        task_type: str = "freelancing"
    ) -> bool:
        """Save a successful experience to the gallery."""
        if not self.connected:
            return False
            
        try:
            body = {
                "user_id": user_id,
                "task_type": task_type,
                "input_query": task,
                "outcome": outcome,
                "lesson": lesson,
                "feedback_score": score,
                "is_public": score > 0,
                "created_at": datetime.datetime.utcnow().isoformat()
            }
            
            self.client.index(index=self.GALLERY_INDEX, body=body)
            logger.info(f"Saved experience from user {user_id}")
            
            # If positive, also contribute to global wisdom
            if score > 0:
                await self._contribute_to_wisdom(task_type, lesson)
            
            return True
        except Exception as e:
            logger.error(f"Error saving experience: {e}")
            return False
    
    async def search_similar_experiences(
        self,
        query: str,
        limit: int = 5,
        task_type: str = None
    ) -> List[Dict]:
        """Search for similar experiences in the gallery."""
        if not self.connected:
            return []
            
        try:
            must = [
                {"multi_match": {"query": query, "fields": ["input_query", "lesson", "outcome"]}},
                {"term": {"is_public": True}}
            ]
            
            if task_type:
                must.append({"term": {"task_type": task_type}})
            
            res = self.client.search(
                index=self.GALLERY_INDEX,
                body={
                    "size": limit,
                    "query": {"bool": {"must": must}},
                    "sort": [{"feedback_score": "desc"}]
                }
            )
            
            return [hit["_source"] for hit in res.get("hits", {}).get("hits", [])]
        except Exception as e:
            logger.error(f"Error searching experiences: {e}")
            return []
    
    # ==========================================
    # Global Wisdom Methods
    # ==========================================
    
    async def _contribute_to_wisdom(self, category: str, insight: str):
        """Internal: Add/update wisdom from a positive experience."""
        try:
            # Search for similar existing wisdom
            res = self.client.search(
                index=self.WISDOM_INDEX,
                body={
                    "size": 1,
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"category": category}},
                                {"match": {"insight": insight}}
                            ]
                        }
                    }
                }
            )
            
            hits = res.get("hits", {}).get("hits", [])
            
            if hits and hits[0]["_score"] > 5:  # High similarity
                # Update existing
                doc_id = hits[0]["_id"]
                existing = hits[0]["_source"]
                self.client.update(
                    index=self.WISDOM_INDEX,
                    id=doc_id,
                    body={
                        "doc": {
                            "source_count": existing.get("source_count", 1) + 1,
                            "confidence_score": min(1.0, existing.get("confidence_score", 0.5) + 0.1),
                            "last_updated": datetime.datetime.utcnow().isoformat()
                        }
                    }
                )
            else:
                # Create new wisdom
                self.client.index(
                    index=self.WISDOM_INDEX,
                    body={
                        "category": category,
                        "insight": insight,
                        "source_count": 1,
                        "confidence_score": 0.5,
                        "tags": [category],
                        "created_at": datetime.datetime.utcnow().isoformat(),
                        "last_updated": datetime.datetime.utcnow().isoformat()
                    }
                )
        except Exception as e:
            logger.debug(f"Wisdom contribution error (non-critical): {e}")
    
    async def get_global_wisdom(
        self,
        category: str = None,
        query: str = None,
        limit: int = 10,
        min_confidence: float = 0.3
    ) -> List[Dict]:
        """Get global wisdom insights."""
        if not self.connected:
            return []
            
        try:
            must = [{"range": {"confidence_score": {"gte": min_confidence}}}]
            
            if category:
                must.append({"term": {"category": category}})
            
            if query:
                must.append({"match": {"insight": query}})
            
            res = self.client.search(
                index=self.WISDOM_INDEX,
                body={
                    "size": limit,
                    "query": {"bool": {"must": must}},
                    "sort": [
                        {"confidence_score": "desc"},
                        {"source_count": "desc"}
                    ]
                }
            )
            
            return [hit["_source"] for hit in res.get("hits", {}).get("hits", [])]
        except Exception as e:
            logger.error(f"Error getting global wisdom: {e}")
            return []
    
    async def add_wisdom(
        self,
        category: str,
        insight: str,
        tags: List[str] = None,
        confidence: float = 0.5
    ) -> bool:
        """Manually add a wisdom entry."""
        if not self.connected:
            return False
            
        try:
            now = datetime.datetime.utcnow().isoformat()
            self.client.index(
                index=self.WISDOM_INDEX,
                body={
                    "category": category,
                    "insight": insight,
                    "source_count": 1,
                    "confidence_score": confidence,
                    "tags": tags or [category],
                    "created_at": now,
                    "last_updated": now
                }
            )
            logger.info(f"Added wisdom: {category}")
            return True
        except Exception as e:
            logger.error(f"Error adding wisdom: {e}")
            return False
    
    # ==========================================
    # Profile Learning Methods
    # ==========================================
    
    async def summarize_and_update(
        self,
        user_id: str,
        current_profile: str,
        interaction: str
    ):
        """
        Use LLM to synthesize interaction into profile.
        This is how the system 'learns' about the user.
        """
        try:
            from openai import AsyncOpenAI
            from config import settings
            
            client = AsyncOpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL
            )
            
            prompt = f"""
Merge the following NEW INTERACTION into the EXISTING USER PROFILE.
Focus on identifying:
1. Behavioral patterns (e.g., priorities, tone).
2. Rules & Constraints (e.g., job preferences, specific NO-GOs).
3. Important History (e.g., companies mentioned, problems solved).

EXISTING PROFILE:
{current_profile if current_profile else "No previous profile."}

NEW INTERACTION:
{interaction}

Return a concise, bulleted summary (Max 500 words) that will serve as the NEW PROFILE.
Do not include sensitive PII.
"""
            
            response = await client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": "You are a profile synthesis assistant. Create concise user profiles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            
            new_profile = response.choices[0].message.content
            await self.update_user_profile(user_id, summary=new_profile)
            
        except Exception as e:
            logger.error(f"Failed to synthesize profile: {e}")
    
    # ==========================================
    # Health & Status
    # ==========================================
    
    def health_check(self) -> Dict[str, Any]:
        """Check elasticsearch connection health."""
        if not self.client:
            return {"status": "disconnected", "connected": False}
            
        try:
            info = self.client.info()
            return {
                "status": "healthy",
                "connected": True,
                "cluster_name": info.get("cluster_name", "unknown"),
                "version": info.get("version", {}).get("number", "unknown")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, int]:
        """Get document counts for all indices."""
        if not self.connected:
            return {}
            
        try:
            stats = {}
            for index in [self.PROFILE_INDEX, self.CHAT_INDEX, self.GALLERY_INDEX, self.WISDOM_INDEX]:
                try:
                    count = self.client.count(index=index)
                    stats[index] = count.get("count", 0)
                except:
                    stats[index] = 0
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# Singleton instance with lazy initialization
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get or create the singleton MemoryManager."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


# Backward compatibility alias
memory_manager = property(lambda self: get_memory_manager())
