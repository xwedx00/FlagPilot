
import logging
import tiktoken
from typing import Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.base import get_db
from models.intelligence import AgentTask
from lib.credits import CreditService
from .context import current_user_id

logger = logging.getLogger("uvicorn")

class CostManager:
    # Cost in credits per 1k tokens
    # Adjust these rates as needed. 
    # Example: 1 Credit = $0.01 (1 cent)
    # GPT-4o: Input $5/1M ($0.005/1k), Output $15/1M ($0.015/1k)
    # If 1 Credit = $0.01:
    # Input: 0.5 credits/1k
    # Output: 1.5 credits/1k
    
    RATES = {
        "gpt-4": {"input": 3.0, "output": 6.0},
        "gpt-4o": {"input": 0.5, "output": 1.5},
        "gpt-3.5-turbo": {"input": 0.05, "output": 0.15},
        # Default fallback
        "default": {"input": 0.1, "output": 0.3}
    }
    
    _encoders = {}

    @classmethod
    def get_encoder(cls, model: str):
        if model not in cls._encoders:
            try:
                cls._encoders[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                cls._encoders[model] = tiktoken.get_encoding("cl100k_base")
        return cls._encoders[model]

    @classmethod
    def count_tokens(cls, text: str, model: str = "gpt-3.5-turbo") -> int:
        if not text:
            return 0
        encoder = cls.get_encoder(model)
        return len(encoder.encode(text))

    @classmethod
    def calculate_cost(cls, model: str, input_tokens: int, output_tokens: int) -> float:
        rate = cls.RATES.get(model, cls.RATES.get("default"))
        
        input_cost = (input_tokens / 1000) * rate["input"]
        output_cost = (output_tokens / 1000) * rate["output"]
        
        return input_cost + output_cost

    @classmethod
    async def track_and_deduct(cls, model: str, input_text: str, output_text: str, usage_type: str = "llm_call") -> bool:
        """
        Calculates cost and deducts from the CURRENT context user.
        Returns True if successful, False if failed (or no user).
        """
        user_id = current_user_id.get()
        if not user_id:
            logger.warning("CostManager: No user_id in context, skipping deduction.")
            return False
            
        input_tokens = cls.count_tokens(input_text, model)
        output_tokens = cls.count_tokens(output_text, model)
        total_tokens = input_tokens + output_tokens
        
        cost = cls.calculate_cost(model, input_tokens, output_tokens)
        cost_int = int(cost) 
        if cost_int < 1 and cost > 0:
            cost_int = 1 # Minimum 1 credit if usage > 0
            
        if cost_int <= 0:
            return True

        logger.info(f"Billing: {user_id} | {model} | {input_tokens}+{output_tokens}={total_tokens} toks | {cost_int} credits")

        # Deduct from DB
        try:
            # We need a DB session. Since we are deep in the call stack, 
            # we must create a fresh one or pass it. 
            # Ideally, we should pass session, but patching makes that hard.
            # We'll create a new session generator context.
            async for db in get_db():
                description = f"LLM Usage: {model} ({total_tokens} tokens)"
                success = await CreditService.deduct_credits(db, user_id, cost_int, description)
                if not success:
                    logger.warning(f"Billing: User {user_id} insufficient funds for {cost_int} credits.")
                return success
        except Exception as e:
            logger.error(f"Billing Error: {e}")
            return False

