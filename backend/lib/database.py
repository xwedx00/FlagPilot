"""
PostgreSQL Database Connection using SQLAlchemy
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, JSON
from datetime import datetime
from loguru import logger
from typing import Optional

# Global instances
_engine = None
_session_factory = None

# Base class for models
Base = declarative_base()


# ============ Models ============

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=True)
    name = Column(String(255), nullable=True)
    role = Column(String(50), default="user")  # user, freelancer, hr, admin
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Workspace(Base):
    """User workspace with their data"""
    __tablename__ = "workspaces"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)  # Jobs, candidates, contracts, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Task(Base):
    """Task history"""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False)
    workspace_id = Column(String(36), nullable=True)
    task_type = Column(String(100), nullable=False)  # team, single_agent
    input_text = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    agents_used = Column(JSON, nullable=True)  # List of agent IDs
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class Feedback(Base):
    """User feedback on agent responses"""
    __tablename__ = "feedback"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False)
    task_id = Column(String(36), nullable=True)
    agent_id = Column(String(100), nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============ Database Functions ============

async def init_db():
    """Initialize database connection and create tables"""
    global _engine, _session_factory
    
    database_url = os.getenv("DATABASE_URL", "postgresql://flagpilot:flagpilot@localhost:5432/flagpilot")
    
    # Convert to async URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    try:
        _engine = create_async_engine(database_url, echo=False)
        _session_factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
        
        # Create tables
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("PostgreSQL database connected and tables created")
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


async def close_db():
    """Close database connection"""
    global _engine
    if _engine:
        await _engine.dispose()
        logger.info("Database connection closed")


def get_db() -> async_sessionmaker:
    """Get database session factory"""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _session_factory


async def get_session() -> AsyncSession:
    """Get a database session"""
    async with get_db()() as session:
        yield session
