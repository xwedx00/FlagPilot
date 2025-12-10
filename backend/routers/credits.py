from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from auth import get_current_user, UserData
from models import get_db, CreditWallet, CreditTransaction
from lib.credits import CreditService

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
    Get real credit balance from DB via CreditService.
    """
    wallet = await CreditService.get_wallet(db, user.id)
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
    # Using CreditService logic manually for history for now, 
    # or could add get_history to Service. 
    # Keeping direct DB access here is fine for read-only View logic.
    from sqlalchemy import select
    
    wallet = await CreditService.get_wallet(db, user.id)
    
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
async def purchase_credits(amount: int, user: UserData = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Initiate credit purchase.
    FOR DEMO: Adds credits immediately.
    """
    # In production, this would call Stripe/Polar and wait for webhook.
    # For testing, we auto-refill.
    success = await CreditService.add_credits(db, user.id, amount, "Top-up via API")
    if not success:
         raise HTTPException(status_code=500, detail="Purchase failed")
         
    return PurchaseResponse(
        checkoutUrl=f"https://polar.sh/checkout?amount={amount}&user={user.id}"
    )
