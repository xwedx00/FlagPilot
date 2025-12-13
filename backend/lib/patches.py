
import logging
import asyncio
from typing import Union, List, Optional
from metagpt.schema import Message
# Defer imports or keep them if they are safe. OpenAILLM import seemed safe in debug script.
from metagpt.provider.openai_api import OpenAILLM

from lib.cost import CostManager

logger = logging.getLogger("uvicorn")

# Store original method
_original_aask = None

async def cost_aware_aask(self, msg: Union[str, List[dict], List[Message], List[str]], system_msgs: Optional[List[str]] = None, **kwargs) -> str:
    """
    Patched version of OpenAILLM.aask that tracks cost.
    """
    if _original_aask is None:
        # Fallback if patch improperly applied or race condition?
        # Should not happen if apply_patches called.
        # But if we can't find original, we might be in trouble (recursion).
        # We can try to call super().aask if we knew the MRO here, but 'self' is the instance.
        logger.error("Billing Patch Error: _original_aask is None!")
        return "Error: Internal Billing Error"

    # 1. Execute original call
    response_text = await _original_aask(self, msg, system_msgs, **kwargs)
    
    # 2. Calculate Cost
    try:
        # Extract input text
        input_text = ""
        if isinstance(msg, str):
            input_text = msg
        elif isinstance(msg, list):
            for item in msg:
                if isinstance(item, str):
                    input_text += item
                elif isinstance(item, dict):
                    input_text += item.get("content", "")
                elif isinstance(item, Message):
                    input_text += item.content

        if system_msgs:
            for sys_msg in system_msgs:
                 input_text += str(sys_msg)

        # Track usage
        model = getattr(self, "model", "gpt-3.5-turbo")
        
        await CostManager.track_and_deduct(model, input_text, response_text)
        
    except Exception as e:
        logger.error(f"Billing Patch Error: {e}")
        
    return response_text

def apply_metagpt_patches():
    """
    Apply monkey patches to MetaGPT to enable billing.
    """
    global _original_aask
    logger.info("🔧 Applying MetaGPT Billing Patches...")
    
    try:
        # Capture original
        _original_aask = OpenAILLM.aask
        
        # Patch OpenAILLM directly
        OpenAILLM.aask = cost_aware_aask
        
        logger.info("✅ MetaGPT Billing Patch Applied: OpenAILLM.aask -> cost_aware_aask")
    except Exception as e:
        logger.error(f"❌ Failed to apply MetaGPT patches: {e}")
