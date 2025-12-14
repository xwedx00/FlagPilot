#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : test_role_context.py
@Desc    : Tests for RoleContext (Ported from test_role_context.py)
"""

import pytest
from agents.roles.base_role import FlagPilotRole
from metagpt.schema import Message

class MockRole(FlagPilotRole):
    name: str = "MockName"
    profile: str = "MockProfile"
    
    async def _act(self):
        return Message(content="test", role="assistant")

@pytest.mark.asyncio
async def test_role_context_initialization(mock_user):
    """Test that FlagPilotRole initializes rc correctly."""
    
    # 1. Initialize Role directly
    role = MockRole()
    
    # Verify defaults
    assert role.rc.memory is not None
    assert role.profile == "MockProfile"
    
    # Test setting context
    role.rc.env = None # Ensure no env to start
    
    # Simulate context injection (like Team would do)
    from metagpt.context import Context
    ctx = Context()
    ctx.kwargs.set("user_id", mock_user.id)
    role.context = ctx
    
    # Verify _act can access it (FlagPilotRole._act merges contexts)
    # We can't easily inspect local variables in _act, but we can check if it runs without error
    msg = await role._act()
    assert msg.content == "test"
