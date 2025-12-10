
import uuid
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.credits import CreditWallet, CreditTransaction

logger = logging.getLogger("uvicorn")

class CreditService:
    @staticmethod
    async def get_wallet(db: AsyncSession, user_id: str) -> CreditWallet:
        """Get or create user wallet"""
        stmt = select(CreditWallet).where(CreditWallet.user_id == user_id)
        result = await db.execute(stmt)
        wallet = result.scalars().first()
        
        if not wallet:
            logger.info(f"Creating new wallet for user {user_id}")
            wallet = CreditWallet(
                id=str(uuid.uuid4()),
                user_id=user_id,
                balance=50 # Welcome bonus
            )
            db.add(wallet)
            # We don't commit here immediately if caller wants to wrap in transaction?
            # But ensure it exists.
            await db.commit()
            await db.refresh(wallet)
        
        return wallet

    @staticmethod
    async def check_balance(db: AsyncSession, user_id: str, cost: int) -> bool:
        """Check if user has enough credits"""
        wallet = await CreditService.get_wallet(db, user_id)
        return wallet.balance >= cost

    @staticmethod
    async def deduct_credits(db: AsyncSession, user_id: str, cost: int, description: str, reference_id: str = None) -> bool:
        """
        Deduct credits atomically.
        Returns True if successful, False if insufficient funds.
        """
        try:
            wallet = await CreditService.get_wallet(db, user_id)
            
            if wallet.balance < cost:
                return False
                
            wallet.balance -= cost
            
            tx = CreditTransaction(
                id=str(uuid.uuid4()),
                wallet_id=wallet.id,
                amount=-cost, # Negative for deduction
                description=description,
                reference_id=reference_id
            )
            db.add(tx)
            await db.commit()
            logger.info(f"Deducted {cost} credits from {user_id}. New balance: {wallet.balance}")
            return True
        except Exception as e:
            logger.error(f"Credit deduction failed: {e}")
            await db.rollback()
            return False

    @staticmethod
    async def add_credits(db: AsyncSession, user_id: str, amount: int, description: str, reference_id: str = None) -> bool:
        """Add credits to user wallet"""
        try:
            wallet = await CreditService.get_wallet(db, user_id)
            wallet.balance += amount
            
            tx = CreditTransaction(
                id=str(uuid.uuid4()),
                wallet_id=wallet.id,
                amount=amount,
                description=description,
                reference_id=reference_id
            )
            db.add(tx)
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"Credit addition failed: {e}")
            await db.rollback()
            return False
