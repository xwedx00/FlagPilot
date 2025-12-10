from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from auth import get_current_user, UserData
from models import get_db, CreditWallet, CreditTransaction

router = APIRouter(prefix="/api/v1/credits", tags=["credits"])

class CreditBalance(BaseModel):
    current: int
    total: int = 0
    usageThisMonth: int = 0

class CreditTransactionSchema(BaseModel):
    id: str
    amount: int
    description: str
    referenceId: str | None = None
    createdAt: datetime

    class Config:
        from_attributes = True

class PurchaseResponse(BaseModel):
    checkoutUrl: str

@router.get("/balance", response_model=CreditBalance)
async def get_balance(
    user: UserData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get real credit balance from DB.
    Auto-creates wallet if missing (Onboarding logic).
    """
    query = select(CreditWallet).where(CreditWallet.user_id == user.id)
    result = await db.execute(query)
    wallet = result.scalars().first()

    if not wallet:
        # Auto-create wallet for new users
        import uuid
        wallet = CreditWallet(
            id=str(uuid.uuid4()),
            user_id=user.id,
            balance=50 # Welcome bonus
        )
        db.add(wallet)
        await db.commit()
    
    return CreditBalance(current=wallet.balance)

@router.get("/history", response_model=List[CreditTransactionSchema])
async def get_history(
    limit: int = 50, 
    user: UserData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get real credit history.
    """
    # First get wallet
    wallet_query = select(CreditWallet).where(CreditWallet.user_id == user.id)
    result = await db.execute(wallet_query)
    wallet = result.scalars().first()

    if not wallet:
        return []

    # Get transactions
    stmt = (
        select(CreditTransaction)
        .where(CreditTransaction.wallet_id == wallet.id)
        .order_by(CreditTransaction.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    txs = result.scalars().all()
    
    return txs

@router.post("/purchase", response_model=PurchaseResponse)
async def purchase_credits(amount: int, user: UserData = Depends(get_current_user)):
    """
    Initiate credit purchase (Mock for now, returns Polar URL).
    """
    return PurchaseResponse(
        checkoutUrl=f"https://polar.sh/checkout?amount={amount}&user={user.id}"
    )
