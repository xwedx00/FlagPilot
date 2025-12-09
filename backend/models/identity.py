"""
Identity Domain Models

Better Auth compatible schema for split-stack authentication.
The Next.js frontend manages these tables via Better Auth.
The Python backend reads them for session verification.

IMPORTANT: Do not modify these tables from Python - they are managed by Better Auth.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer, ForeignKey, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    """
    User table - Better Auth managed.
    
    Extended with FlagPilot-specific fields for freelancer context.
    """
    __tablename__ = "user"
    
    # Better Auth core fields
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # FlagPilot extensions
    is_freelancer: Mapped[bool] = mapped_column(Boolean, default=True)
    theme_pref: Mapped[str] = mapped_column(String(50), default="mgx-dark")
    onboarding_step: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    sessions: Mapped[list["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    accounts: Mapped[list["Account"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_email", "email"),
    )


class Session(Base):
    """
    Session table - Better Auth managed.
    
    This is the critical table for split-stack authentication.
    Python backend verifies sessions by querying this table directly.
    """
    __tablename__ = "session"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    token: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")
    
    # Indexes for fast token lookup
    __table_args__ = (
        Index("idx_session_token", "token"),
        Index("idx_session_user_id", "user_id"),
        Index("idx_session_expires", "expires_at"),
    )


class Account(Base):
    """
    Account table - Better Auth managed.
    
    Links users to OAuth providers (Google, GitHub, etc.)
    """
    __tablename__ = "account"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    account_id: Mapped[str] = mapped_column(Text, nullable=False)
    provider_id: Mapped[str] = mapped_column(Text, nullable=False)
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    access_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    refresh_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scope: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    id_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    password: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="accounts")
    
    __table_args__ = (
        Index("idx_account_user_id", "user_id"),
        Index("idx_account_provider", "provider_id", "account_id"),
    )


class Verification(Base):
    """
    Verification table - Better Auth managed.
    
    Stores email verification and password reset tokens.
    """
    __tablename__ = "verification"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    identifier: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_verification_identifier", "identifier"),
    )
