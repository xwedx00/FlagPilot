"""
RAG & Memory Tools
==================
Shared tools for all agents - knowledge base search, user context, and learning.
"""

from typing import Optional, List, Dict, Any
from langchain.tools import tool
from pydantic import BaseModel, Field
from loguru import logger

from .base import track_tool, ToolResult


# =============================================================================
# Input Schemas
# =============================================================================

class KnowledgeSearchInput(BaseModel):
    """Input for knowledge base search."""
    query: str = Field(..., description="Search query for the knowledge base")
    k: int = Field(default=5, description="Number of results to return", ge=1, le=20)
    user_id: Optional[str] = Field(None, description="Filter by user ID")


class UserContextInput(BaseModel):
    """Input for user context retrieval."""
    user_id: str = Field(..., description="User ID to fetch context for")
    include_history: bool = Field(default=True, description="Include chat history")
    include_profile: bool = Field(default=True, description="Include user profile")


class SaveLearningInput(BaseModel):
    """Input for saving a learning to experience gallery."""
    user_id: str = Field(..., description="User ID")
    task: str = Field(..., description="What was the task/problem")
    outcome: str = Field(..., description="What was the outcome (success/failure)")
    lesson: str = Field(..., description="Key lesson learned")
    category: str = Field(default="general", description="Category: contract, scam, negotiation, etc")


# =============================================================================
# Tools
# =============================================================================

@tool(args_schema=KnowledgeSearchInput)
@track_tool
async def search_knowledge_base(
    query: str,
    k: int = 5,
    user_id: Optional[str] = None
) -> str:
    """
    Search the FlagPilot knowledge base for relevant information.
    Uses Qdrant vector search with OpenAI embeddings.
    Returns relevant documents about freelancing, contracts, scams, and best practices.
    """
    try:
        from lib.rag import get_rag_pipeline
        
        pipeline = get_rag_pipeline()
        docs = await pipeline.retrieve(query=query, k=k, user_id=user_id)
        
        if not docs:
            return "No relevant documents found in knowledge base."
        
        results = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            content = doc.page_content[:500]
            results.append(f"[{i}] Source: {source}\n{content}")
        
        return "\n\n---\n\n".join(results)
        
    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        return f"Knowledge search unavailable: {str(e)}"


@tool(args_schema=UserContextInput)
@track_tool
async def get_user_context(
    user_id: str,
    include_history: bool = True,
    include_profile: bool = True
) -> str:
    """
    Retrieve personalized context for a user including their profile and chat history.
    Helps agents provide personalized recommendations based on user's past interactions.
    """
    try:
        from lib.memory.manager import MemoryManager
        
        memory = MemoryManager()
        context_parts = []
        
        if include_profile and memory.connected:
            profile = await memory.get_user_profile(user_id)
            if profile.get("summary"):
                context_parts.append(f"**User Profile:**\n{profile['summary']}")
            if profile.get("preferences"):
                prefs = profile["preferences"]
                context_parts.append(f"**Preferences:** {prefs}")
        
        if include_history and memory.connected:
            history = await memory.get_chat_history(user_id, limit=5)
            if history:
                recent = [f"- {h.get('role', 'user')}: {h.get('content', '')[:100]}..." for h in history[:3]]
                context_parts.append(f"**Recent Conversations:**\n" + "\n".join(recent))
        
        if not context_parts:
            return "No user context available. This may be a new user."
        
        return "\n\n".join(context_parts)
        
    except Exception as e:
        logger.error(f"User context retrieval failed: {e}")
        return f"User context unavailable: {str(e)}"


@tool(args_schema=SaveLearningInput)
@track_tool
async def save_learning(
    user_id: str,
    task: str,
    outcome: str,
    lesson: str,
    category: str = "general"
) -> str:
    """
    Save a learning or insight to the experience gallery.
    These learnings are anonymized and can help improve recommendations for all users.
    """
    try:
        from lib.memory.manager import MemoryManager
        
        memory = MemoryManager()
        
        if not memory.connected:
            return "Memory system unavailable. Learning not saved."
        
        # Save to experience gallery
        await memory.save_experience(
            user_id=user_id,
            task=task,
            outcome=outcome,
            lesson=lesson,
            task_type=category
        )
        
        # If it's a successful outcome, contribute to global wisdom
        if "success" in outcome.lower():
            await memory.add_wisdom(
                category=category,
                insight=lesson,
                tags=[category, "user_contributed"],
                confidence=0.5  # User-contributed starts at 50%
            )
        
        return f"✅ Learning saved to experience gallery.\nCategory: {category}\nLesson: {lesson[:100]}..."
        
    except Exception as e:
        logger.error(f"Save learning failed: {e}")
        return f"Failed to save learning: {str(e)}"


# =============================================================================
# Tool Registry
# =============================================================================

RAG_TOOLS = [
    search_knowledge_base,
    get_user_context,
    save_learning,
]
