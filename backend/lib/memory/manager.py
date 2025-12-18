
from elasticsearch import Elasticsearch
from loguru import logger
from config import settings
from typing import Optional, List, Dict, Any
import datetime

class MemoryManager:
    """
    Manages the Triple-Tiered Memory system:
    1. Dynamic User Profiles (Personal)
    2. Experience Gallery (Shared/Anonymized)
    """

    def __init__(self):
        self.es_url = f"http://{settings.ES_HOST}:{settings.ES_PORT}"
        self.client = Elasticsearch(self.es_url)
        self.profile_index = "flagpilot_user_profiles"
        self.gallery_index = "flagpilot_experience_gallery"
        
        # Initialize indices
        self._ensure_indices()

    def _ensure_indices(self):
        """Create indices if they don't exist."""
        try:
            if not self.client.indices.exists(index=self.profile_index):
                self.client.indices.create(index=self.profile_index, body={
                    "mappings": {
                        "properties": {
                            "user_id": {"type": "keyword"},
                            "summary": {"type": "text"},
                            "preferences": {"type": "object"},
                            "last_updated": {"type": "date"}
                        }
                    }
                })
                logger.info(f"Created index: {self.profile_index}")

            if not self.client.indices.exists(index=self.gallery_index):
                self.client.indices.create(index=self.gallery_index, body={
                    "mappings": {
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
                    }
                })
                logger.info(f"Created index: {self.gallery_index}")
        except Exception as e:
            logger.error(f"Failed to ensure indices: {e}")

    async def get_current_user_profile(self, user_id: str) -> str:
        """Retrieve the dynamic profile summary for a user."""
        try:
            res = self.client.get(index=self.profile_index, id=user_id, ignore=[404])
            if res.get("found"):
                return res["_source"].get("summary", "")
            return "" # No profile yet
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return ""

    async def update_user_profile(self, user_id: str, new_summary: str):
        """Update the user's live profile summary."""
        try:
            body = {
                "user_id": user_id,
                "summary": new_summary,
                "last_updated": datetime.datetime.utcnow().isoformat()
            }
            self.client.index(index=self.profile_index, id=user_id, body=body)
            logger.info(f"Updated dynamic profile for user: {user_id}")
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")

    async def summarize_and_update(self, user_id: str, current_profile: str, interaction: str):
        """
        Uses an LLM to synthesize a new interaction into the existing profile.
        This is how the system 'learns' about the user.
        """
        try:
            from config import get_configured_llm
            llm = get_configured_llm()
            
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
            new_profile = await llm.aask(prompt)
            await self.update_user_profile(user_id, new_profile)
            
        except Exception as e:
            logger.error(f"Failed to synthesize profile: {e}")

    async def save_experience(self, user_id: str, task: str, outcome: str, lesson: str, score: int = 1):
        """Save a successful interaction to the gallery."""
        try:
            body = {
                "user_id": user_id,
                "task_type": "freelancing", # Placeholder
                "input_query": task,
                "outcome": outcome,
                "lesson": lesson,
                "feedback_score": score,
                "is_public": score > 0, # Auto-publish if positive feedback
                "created_at": datetime.datetime.utcnow().isoformat()
            }
            self.client.index(index=self.gallery_index, body=body)
            logger.info(f"Saved experience from user {user_id} to gallery.")
        except Exception as e:
            logger.error(f"Error saving experience: {e}")

    async def search_similar_experiences(self, query: str, limit: int = 3) -> List[Dict]:
        """
        Search for similar successful cases.
        For now, uses BM25 text search (Full-text). 
        Future: Use dense vector search with OpenAI embeddings.
        """
        try:
            res = self.client.search(index=self.gallery_index, body={
                "size": limit,
                "query": {
                    "bool": {
                        "must": [
                            {"multi_match": {"query": query, "fields": ["input_query", "lesson"]}},
                            {"term": {"is_public": True}}
                        ]
                    }
                }
            })
            return [hit["_source"] for hit in res.get("hits", {}).get("hits", [])]
        except Exception as e:
            logger.error(f"Error searching experiences: {e}")
            return []

# Singleton
memory_manager = MemoryManager()
