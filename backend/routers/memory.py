"""
Memory API Router
==================
Provides API endpoints for the memory system:
- User profiles
- Chat history / sessions
- Global wisdom
- Experience gallery
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from loguru import logger

from lib.auth.middleware import get_current_user, get_optional_user
from lib.memory.manager import get_memory_manager

router = APIRouter(prefix="/api/memory", tags=["Memory"])


# ============================================
# Response Models
# ============================================

class WisdomInsight(BaseModel):
    category: str
    insight: str
    confidence_score: float
    source_count: int
    tags: List[str] = []


class ChatSession(BaseModel):
    session_id: str
    timestamp: str
    message_count: int
    preview: str


class UserProfile(BaseModel):
    user_id: str
    summary: str
    preferences: Dict[str, Any] = {}
    risk_tolerance: Optional[str] = None
    last_updated: Optional[str] = None


# ============================================
# Wisdom Endpoints
# ============================================

@router.get("/wisdom", response_model=List[WisdomInsight])
async def get_global_wisdom(
    category: Optional[str] = Query(None, description="Filter by category"),
    query: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    min_confidence: float = Query(0.3, ge=0, le=1)
):
    """
    Get global wisdom insights from the community knowledge base.
    Returns anonymized, aggregated learnings from all users.
    """
    try:
        memory = get_memory_manager()
        
        if not memory.connected:
            # Return sample wisdom when ES is not connected
            logger.warning("ES not connected, returning sample wisdom")
            return [
                WisdomInsight(
                    category="contracts",
                    insight="Always get a deposit before starting work - 30-50% upfront is standard.",
                    confidence_score=0.95,
                    source_count=847,
                    tags=["contracts", "payment"]
                ),
                WisdomInsight(
                    category="negotiation",
                    insight="Anchor high in negotiations - your first number sets the range.",
                    confidence_score=0.88,
                    source_count=523,
                    tags=["negotiation", "rates"]
                ),
                WisdomInsight(
                    category="scams",
                    insight="Be wary of clients who want to move communication off-platform immediately.",
                    confidence_score=0.92,
                    source_count=1204,
                    tags=["scams", "safety"]
                ),
            ]
        
        wisdom = await memory.get_global_wisdom(
            category=category,
            query=query,
            limit=limit,
            min_confidence=min_confidence
        )
        
        return [
            WisdomInsight(
                category=w.get("category", "general"),
                insight=w.get("insight", ""),
                confidence_score=w.get("confidence_score", 0.5),
                source_count=w.get("source_count", 1),
                tags=w.get("tags", [])
            )
            for w in wisdom
        ]
        
    except Exception as e:
        logger.error(f"Failed to get wisdom: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve wisdom")


# ============================================
# Profile Endpoints
# ============================================

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    user_id: str = Depends(get_current_user)
):
    """
    Get the current user's profile with learned preferences.
    """
    try:
        memory = get_memory_manager()
        
        if not memory.connected or user_id == "anonymous":
            return UserProfile(
                user_id=user_id,
                summary="",
                preferences={},
                risk_tolerance=None
            )
        
        profile = await memory.get_user_profile(user_id)
        
        return UserProfile(
            user_id=user_id,
            summary=profile.get("summary", ""),
            preferences=profile.get("preferences", {}),
            risk_tolerance=profile.get("risk_tolerance"),
            last_updated=profile.get("last_updated")
        )
        
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")


# ============================================
# Session Endpoints
# ============================================

@router.get("/sessions", response_model=List[ChatSession])
async def get_recent_sessions(
    user_id: str = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get recent chat sessions for the current user.
    """
    try:
        memory = get_memory_manager()
        
        if not memory.connected or user_id == "anonymous":
            return []
        
        session_ids = await memory.get_recent_sessions(user_id, limit=limit)
        
        sessions = []
        for sid in session_ids[:limit]:
            # Get first message as preview
            history = await memory.get_chat_history(user_id, session_id=sid, limit=1)
            preview = history[0].get("content", "")[:50] + "..." if history else "Empty session"
            
            sessions.append(ChatSession(
                session_id=sid,
                timestamp=history[0].get("timestamp", "") if history else "",
                message_count=len(history),
                preview=preview
            ))
        
        return sessions
        
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")


# ============================================
# Health Check
# ============================================

@router.get("/health")
async def memory_health():
    """Check memory system health."""
    memory = get_memory_manager()
    return {
        "status": "healthy" if memory.connected else "degraded",
        "connected": memory.connected,
        "stats": memory.get_stats() if memory.connected else {}
    }
