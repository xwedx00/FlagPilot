"""
Credit System Models
====================
Tracks user credit balance and consumption.
Shared schema ownership (Backend writes usage, Frontend writes purchases).
"""

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class CreditWallet(Base):
    """
    User's Credit Balance.
    One-to-One with User.
    """
    __tablename__ = "credit_wallet"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    balance: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CreditTransaction(Base):
    """
    Ledger of all credit movements.
    """
    __tablename__ = "credit_transaction"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    wallet_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("credit_wallet.id", ondelete="CASCADE"),
        nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False) # Positive for purchase, Negative for usage
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String(36), nullable=True) # e.g. AgentTask ID or Payment ID
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
