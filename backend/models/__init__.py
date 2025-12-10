"""
FlagPilot Database Models

Core schema:
- Identity Domain (User reference from frontend)
- Intelligence Domain (Agent State, Missions, Chat)
"""

from .base import Base, get_db, engine, async_session
from .identity import User, Session, Account
from .intelligence import (
    Project, AgentTask, AgentMemory, TaskStatus, 
    Workflow, Document, Mission, ChatMessage, MissionStatus
)
from .credits import CreditWallet, CreditTransaction

__all__ = [
    "Base",
    "get_db",
    "engine",
    "async_session",
    # Identity
    "User",
    "Session",
    "Account",
    # Intelligence
    "Project",
    "AgentTask",
    "AgentMemory",
    "TaskStatus",
    "Workflow",
    "Document",
    "Mission",
    "ChatMessage",
    "MissionStatus",
    # Credits
    "CreditWallet",
    "CreditTransaction",
]
