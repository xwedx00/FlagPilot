#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : test_planner.py
@Desc    : Tests for Planning Agent (Planner & PlanningRole)
"""

import pytest
import asyncio
from unittest.mock import patch

from metagpt.schema import Message
from agents.roles.planner_role import PlanningRole

# Define a dummy class that behaves like the Action but returns fixed JSON
class DummyWritePlan:
    name: str = "DummyWritePlan"
    
    async def run(self, *args, **kwargs):
        # We simulate a plan with 2 tasks
        return """
        [
            {
                "task_id": "1",
                "dependent_task_ids": [],
                "instruction": "Step 1: Research",
                "assignee": "",
                "task_type": "other"
            },
            {
                "task_id": "2",
                "dependent_task_ids": ["1"],
                "instruction": "Step 2: Summarize",
                "assignee": "",
                "task_type": "other"
            }
        ]
        """

@patch("lib.strategy.planner.WritePlan")
@pytest.mark.asyncio
async def test_planning_role_loop(MockWritePlan, mock_user):
    """
    Verify that PlanningRole:
    1. Accepts a goal
    2. Generates a plan (mocked)
    3. Iterates through the tasks
    4. Completes successfully
    """
    
    # Make the Mock return our Dummy instance
    MockWritePlan.return_value = DummyWritePlan()
    # Mocking attributes needed for serialization/logging if accessed
    MockWritePlan.__name__ = "WritePlan"
    MockWritePlan.__module__ = "actions.planning.write_plan"

    # Initialize Role
    role = PlanningRole()
    
    # Trigger with a goal
    goal_msg = Message(content="Research and summarize AI trends", role="user")
    role.rc.memory.add(goal_msg)
    
    # Act
    # In the new test structure, _act should work just the same
    result_msg = await role._act()
    
    # Verify
    assert result_msg is not None
    assert "Executed Step 1: Research" in result_msg.content
    assert "Executed Step 2: Summarize" in result_msg.content
    
    # Verify Plan State
    assert len(role.planner.plan.get_finished_tasks()) == 2
