"""
Intelligence Domain Models

Agent state persistence for the 13 MetaGPT agents.
Tracks projects, tasks, and agent memory.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import (
    String, Text, Integer, Float, DateTime, ForeignKey, Index, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import Base


class TaskStatus(str, Enum):
    """Status of an agent task"""
    QUEUED = "queued"
    THINKING = "thinking"
    WORKING = "working"
    WAITING_INPUT = "waiting_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class AgentRole(str, Enum):
    """The 13 FlagPilot agents"""
    FLAGPILOT = "flagpilot"           # Orchestrator
    CONTRACT_GUARDIAN = "contract-guardian"  # Legal Eagle
    JOB_AUTHENTICATOR = "job-authenticator"
    PAYMENT_ENFORCER = "payment-enforcer"
    TALENT_VET = "coach"
    GHOSTING_SHIELD = "connector"
    SCOPE_SENTINEL = "scope-sentinel"
    DISPUTE_MEDIATOR = "adjudicator"
    PROFILE_ANALYZER = "coach"
    COMMUNICATION_COACH = "connector"
    NEGOTIATION_ASSISTANT = "negotiator"
    APPLICATION_FILTER = "job-authenticator"
    FEEDBACK_LOOP = "scribe"
    IRIS = "iris"                     # Deep Research
    SENTINEL = "sentinel"             # Privacy Officer
    LEDGER = "ledger"                 # Finance
    VAULT_KEEPER = "vault-keeper"     # File Manager


class Project(Base):
    """
    Top-level container for a freelancer's gig or client interaction.
    
    Groups related tasks, documents, and agent memories.
    """
    __tablename__ = "project"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Project details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    client_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Storage path
    minio_path: Mapped[str] = mapped_column(Text, nullable=False)  # users/{id}/projects/{id}
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="active")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks: Mapped[list["AgentTask"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_project_user_id", "user_id"),
        Index("idx_project_status", "status"),
    )


class AgentTask(Base):
    """
    Individual unit of work performed by an agent.
    
    Tracks the full lifecycle from queue to completion.
    """
    __tablename__ = "agent_task"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.id", ondelete="SET NULL"),
        nullable=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Task details
    agent_role: Mapped[str] = mapped_column(String(50), nullable=False)  # Maps to AgentRole
    status: Mapped[TaskStatus] = mapped_column(
        String(50),
        default=TaskStatus.QUEUED.value
    )
    
    # Input/Output
    input_context: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    output_artifact: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Cost tracking
    cost_credits: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    project: Mapped[Optional["Project"]] = relationship(back_populates="tasks")
    memories: Mapped[list["AgentMemory"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_task_user_id", "user_id"),
        Index("idx_task_project_id", "project_id"),
        Index("idx_task_status", "status"),
        Index("idx_task_agent_role", "agent_role"),
    )
    
    def start(self):
        """Mark task as started"""
        self.status = TaskStatus.WORKING.value
        self.started_at = datetime.utcnow()
    
    def complete(self, output: Dict[str, Any]):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED.value
        self.output_artifact = output
        self.completed_at = datetime.utcnow()
    
    def fail(self, error: str):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED.value
        self.error_message = error
        self.completed_at = datetime.utcnow()


class AgentMemory(Base):
    """
    Long-term memory storage for agents.
    
    Stores semantic facts learned during task execution.
    Used for context retrieval in future tasks.
    """
    __tablename__ = "agent_memory"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_task.id", ondelete="SET NULL"),
        nullable=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Memory content
    agent_role: Mapped[str] = mapped_column(String(50), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)  # Semantic key
    value: Mapped[str] = mapped_column(Text, nullable=False)        # The memorized fact
    
    # Metadata
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    memory_type: Mapped[str] = mapped_column(String(50), default="fact")  # fact, preference, constraint
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # For temporary memories
    
    # Relationships
    task: Mapped[Optional["AgentTask"]] = relationship(back_populates="memories")
    
    __table_args__ = (
        Index("idx_memory_user_id", "user_id"),
        Index("idx_memory_agent_role", "agent_role"),
        Index("idx_memory_key", "key"),
    )


class Document(Base):
    """
    Document metadata for files in MinIO.
    
    The actual file content is in MinIO.
    This table stores metadata and processing status.
    """
    __tablename__ = "document"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # File info
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # MinIO location
    bucket: Mapped[str] = mapped_column(String(100), nullable=False)
    object_key: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Processing status
    processing_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, processing, ready, failed
    embedding_status: Mapped[str] = mapped_column(String(50), default="pending")   # pending, embedded, failed
    
    # Extracted data
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)  # Renamed from 'metadata' - reserved by SQLAlchemy
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    __table_args__ = (
        Index("idx_document_user_id", "user_id"),
        Index("idx_document_project_id", "project_id"),
        Index("idx_document_status", "processing_status"),
    )


class Workflow(Base):
    """
    Custom workflow definitions (DAGs) created by users or LLMs.
    """
    __tablename__ = "workflow"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Workflow details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # DAG Definition (stored as JSON)
    # { "nodes": [...], "edges": [...] }
    definition: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    # Metadata
    is_public: Mapped[bool] = mapped_column(default=False)
    tags: Mapped[Optional[list[str]]] = mapped_column(JSONB, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_workflow_user_id", "user_id"),
    )


class MissionStatus(str, Enum):
    """Status of a mission/chat session"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Mission(Base):
    """
    A chat/mission session between the user and FlagPilot agents.
    
    Persists chat history and mission state.
    """
    __tablename__ = "mission"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Mission details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=MissionStatus.ACTIVE.value)
    
    # Workflow data (DAG nodes/edges for visualization)
    workflow_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="mission", 
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )
    
    __table_args__ = (
        Index("idx_mission_user_id", "user_id"),
        Index("idx_mission_status", "status"),
        Index("idx_mission_created_at", "created_at"),
    )


class ChatMessage(Base):
    """
    Individual message in a mission chat.
    
    Stores user messages, agent responses, and system messages.
    """
    __tablename__ = "chat_message"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mission.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Message content
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Agent attribution (if from an agent)
    agent_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Message metadata
    message_type: Mapped[str] = mapped_column(String(50), default="text")  # text, ui_component, workflow_update
    message_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    mission: Mapped["Mission"] = relationship(back_populates="messages")
    
    __table_args__ = (
        Index("idx_chat_message_mission_id", "mission_id"),
        Index("idx_chat_message_user_id", "user_id"),
        Index("idx_chat_message_created_at", "created_at"),
    )
