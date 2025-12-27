"""
Credits Service - Real Credit System
=====================================
Handles credit checking, deduction, and balance management.
NO MOCKS. Production-ready implementation.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from loguru import logger
import asyncpg

from lib.auth.database import DatabasePool


# Credit costs per agent (defined in backend/agents/agents.py)
AGENT_CREDIT_COSTS = {
    "contract-guardian": 15,
    "job-authenticator": 10,
    "scope-sentinel": 8,
    "payment-enforcer": 10,
    "risk-advisor": 12,
    "communication-coach": 8,
    "negotiation-assistant": 12,
    "dispute-mediator": 15,
    "ghosting-shield": 5,
    "profile-analyzer": 8,
    "application-filter": 10,
    "talent-vet": 10,
    "feedback-loop": 3,
    "planner-role": 8,
    "wisdom-search": 5,
    "experience-search": 5,
    "knowledge-search": 5,
}

# Tier limits
TIER_LIMITS = {
    "free": {"monthly_credits": 100, "agents_per_request": 3},
    "starter": {"monthly_credits": 500, "agents_per_request": 5},
    "professional": {"monthly_credits": 2000, "agents_per_request": 10},
    "enterprise": {"monthly_credits": 10000, "agents_per_request": 17},
}


class CreditsService:
    """
    Real credits management service.
    Handles checking, deducting, and resetting credits.
    """
    
    @staticmethod
    async def get_user_credits(user_id: str) -> Dict[str, Any]:
        """
        Get user's current credit balance and limits.
        """
        try:
            pool = await DatabasePool.get_pool()
            
            row = await pool.fetchrow(
                """
                SELECT 
                    credits_balance,
                    credits_used_this_month,
                    credits_reset_at,
                    subscription_tier,
                    role
                FROM "user"
                WHERE id = $1
                """,
                user_id
            )
            
            if not row:
                logger.warning(f"User {user_id} not found for credits check")
                return {
                    "balance": 0,
                    "used_this_month": 0,
                    "tier": "free",
                    "monthly_limit": TIER_LIMITS["free"]["monthly_credits"],
                }
            
            tier = row["subscription_tier"] or "free"
            tier_config = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
            
            return {
                "balance": row["credits_balance"] or 0,
                "used_this_month": row["credits_used_this_month"] or 0,
                "tier": tier,
                "role": row["role"] or "user",
                "monthly_limit": tier_config["monthly_credits"],
                "agents_per_request": tier_config["agents_per_request"],
                "reset_at": row["credits_reset_at"].isoformat() if row["credits_reset_at"] else None,
            }
            
        except Exception as e:
            logger.error(f"Error getting credits for {user_id}: {e}")
            return {"balance": 0, "tier": "free", "monthly_limit": 100}
    
    @staticmethod
    async def check_credits(user_id: str, agent_ids: list[str]) -> Dict[str, Any]:
        """
        Check if user has enough credits for the requested agents.
        Returns check result with cost breakdown.
        """
        user_credits = await CreditsService.get_user_credits(user_id)
        
        # Calculate total cost
        total_cost = sum(
            AGENT_CREDIT_COSTS.get(agent_id, 10) 
            for agent_id in agent_ids
        )
        
        # Check number of agents against tier limit
        max_agents = user_credits.get("agents_per_request", 3)
        if len(agent_ids) > max_agents:
            return {
                "allowed": False,
                "reason": f"Your tier allows max {max_agents} agents per request. "
                         f"Upgrade to use more agents.",
                "cost": total_cost,
                "balance": user_credits["balance"],
            }
        
        # Check credit balance
        if user_credits["balance"] < total_cost:
            return {
                "allowed": False,
                "reason": f"Insufficient credits. Need {total_cost}, have {user_credits['balance']}. "
                         f"Purchase more credits or upgrade your tier.",
                "cost": total_cost,
                "balance": user_credits["balance"],
            }
        
        return {
            "allowed": True,
            "cost": total_cost,
            "balance": user_credits["balance"],
            "new_balance": user_credits["balance"] - total_cost,
        }
    
    @staticmethod
    async def deduct_credits(user_id: str, agent_ids: list[str]) -> Dict[str, Any]:
        """
        Deduct credits for agent usage.
        Returns new balance and usage stats.
        """
        try:
            pool = await DatabasePool.get_pool()
            
            total_cost = sum(
                AGENT_CREDIT_COSTS.get(agent_id, 10) 
                for agent_id in agent_ids
            )
            
            # Atomic update with returning
            row = await pool.fetchrow(
                """
                UPDATE "user"
                SET 
                    credits_balance = credits_balance - $2,
                    credits_used_this_month = credits_used_this_month + $2,
                    total_agent_calls = total_agent_calls + $3,
                    last_agent_call_at = NOW(),
                    updated_at = NOW()
                WHERE id = $1 AND credits_balance >= $2
                RETURNING credits_balance, credits_used_this_month, total_agent_calls
                """,
                user_id, total_cost, len(agent_ids)
            )
            
            if not row:
                logger.warning(f"Failed to deduct credits for {user_id} - insufficient balance")
                return {"success": False, "reason": "Insufficient credits"}
            
            logger.info(
                f"Credits deducted: user={user_id}, cost={total_cost}, "
                f"new_balance={row['credits_balance']}"
            )
            
            return {
                "success": True,
                "cost": total_cost,
                "new_balance": row["credits_balance"],
                "used_this_month": row["credits_used_this_month"],
                "total_calls": row["total_agent_calls"],
            }
            
        except Exception as e:
            logger.error(f"Error deducting credits: {e}")
            return {"success": False, "reason": str(e)}
    
    @staticmethod
    async def add_credits(user_id: str, amount: int, reason: str = "purchase") -> Dict[str, Any]:
        """
        Add credits to user account.
        Used for purchases, bonuses, or refunds.
        """
        try:
            pool = await DatabasePool.get_pool()
            
            row = await pool.fetchrow(
                """
                UPDATE "user"
                SET 
                    credits_balance = credits_balance + $2,
                    updated_at = NOW()
                WHERE id = $1
                RETURNING credits_balance
                """,
                user_id, amount
            )
            
            if not row:
                return {"success": False, "reason": "User not found"}
            
            logger.info(f"Credits added: user={user_id}, amount={amount}, reason={reason}")
            
            return {
                "success": True,
                "added": amount,
                "new_balance": row["credits_balance"],
            }
            
        except Exception as e:
            logger.error(f"Error adding credits: {e}")
            return {"success": False, "reason": str(e)}
    
    @staticmethod
    async def reset_monthly_credits(user_id: str) -> Dict[str, Any]:
        """
        Reset monthly credit usage counter.
        Called by monthly cron job or on subscription renewal.
        """
        try:
            pool = await DatabasePool.get_pool()
            
            # Get tier to determine monthly allocation
            user_info = await pool.fetchrow(
                'SELECT subscription_tier FROM "user" WHERE id = $1',
                user_id
            )
            
            if not user_info:
                return {"success": False, "reason": "User not found"}
            
            tier = user_info["subscription_tier"] or "free"
            monthly_credits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])["monthly_credits"]
            
            await pool.execute(
                """
                UPDATE "user"
                SET 
                    credits_balance = $2,
                    credits_used_this_month = 0,
                    credits_reset_at = NOW(),
                    updated_at = NOW()
                WHERE id = $1
                """,
                user_id, monthly_credits
            )
            
            logger.info(f"Monthly credits reset: user={user_id}, new_balance={monthly_credits}")
            
            return {
                "success": True,
                "new_balance": monthly_credits,
            }
            
        except Exception as e:
            logger.error(f"Error resetting credits: {e}")
            return {"success": False, "reason": str(e)}


# Singleton instance
credits_service = CreditsService()
