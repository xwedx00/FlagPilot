
import asyncio
import logging
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Configure logging
logging.basicConfig(level=logging.INFO)

# 0. Setup Env
sys.path.append(os.getcwd())
try:
    from config import settings
    settings.configure_metagpt_env()
    print("✅ Environment Configured")
except Exception as e:
    print(f"⚠️ Env Config Failed: {e}")

# Mock context
from lib.context import current_user_id
from lib.cost import CostManager
# Import patches AFTER env setup because it imports MetaGPT
from lib.patches import cost_aware_aask, _original_aask
from metagpt.provider.openai_api import OpenAILLM

async def main():
    print("--- Starting Verification ---")
    
    # 1. Test CostManager
    print("Testing CostManager...")
    toks = CostManager.count_tokens("Hello World")
    print(f"Tokens: {toks}")
    assert toks > 0
    cost = CostManager.calculate_cost("gpt-3.5-turbo", 1000, 1000)
    print(f"Cost (1k/1k gpt-3.5): {cost}")
    assert cost > 0

    # 2. Test Patch Logic
    print("Testing Patch Logic...")
    
    # Mock usage deduction to avoid DB calls
    original_track = CostManager.track_and_deduct
    CostManager.track_and_deduct = AsyncMock(return_value=True)
    
    # Mock original aask to avoid OpenAI usage
    import lib.patches
    lib.patches._original_aask = AsyncMock(return_value="Mocked Response")
    
    try:
        llm = OpenAILLM()
        # Ensure model is set (OpenAILLM might load from env)
        if not hasattr(llm, "model") or not llm.model:
             llm.model = "gpt-3.5-turbo"
        
        print(f"LLM Model: {llm.model}")
        
        # Set context
        token = current_user_id.set("test_user_verify")
        
        print("Calling cost_aware_aask...")
        response = await cost_aware_aask(llm, "Input Message")
        print(f"Response: {response}")
        
        print("Verifying Billing Call...")
        CostManager.track_and_deduct.assert_called_once()
        args = CostManager.track_and_deduct.call_args[0]
        print(f"Billing Args: {args}")
        assert args[0] == llm.model
        assert args[2] == "Mocked Response"
        
        print("✅ SUCCESS: Billing logic verified.")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'token' in locals():
            current_user_id.reset(token)
        CostManager.track_and_deduct = original_track

if __name__ == "__main__":
    asyncio.run(main())
