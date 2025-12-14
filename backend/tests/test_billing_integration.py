
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from lib.cost import CostManager
from lib.patches import cost_aware_aask
from lib.context import current_user_id
from metagpt.provider.openai_api import OpenAILLM

@pytest.mark.asyncio
async def test_patch_deduces_credits():
    """Test that the patched aask method calls track_and_deduct"""
    
    # Setup
    from metagpt.config2 import Config
    llm = OpenAILLM(config=Config.default())
    # Mock the original aask logic inside our patch wrapper
    # Since we replaced OpenAILLM.aask globally in the app, 
    # but here in test we need to be careful.
    
    # In this test file, we import cost_aware_aask from lib.patches directly
    # and we can test IT.
    
    with patch("lib.patches._original_aask", new=AsyncMock(return_value="Mock Response")) as mock_orig:
        with patch("lib.cost.CostManager.track_and_deduct", new=AsyncMock(return_value=True)) as mock_track:
            
            token = current_user_id.set("user_123")
            try:
                # Execute patched method explicitly
                response = await cost_aware_aask(llm, "Input Message")
                
                assert response == "Mock Response"
                mock_orig.assert_called_once()  # Should call the original
                mock_track.assert_called_once() # Should call billing
            finally:
                current_user_id.reset(token)
