from __future__ import annotations

from typing import List, Optional

from metagpt.schema import Message
from agents.roles.base_role import FlagPilotRole
from lib.strategy.planner import Planner
from loguru import logger

class PlanningRole(FlagPilotRole):
    name: str = "PlanningAgent"
    profile: str = "Planner"
    goal: str = "Break down complex goals into actionable tasks and execute them."
    constraints: str = "Ensure logical task order and validity."
    
    planner: Optional[Planner] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize planner with empty goal, will update on receive
        self.planner = Planner(goal="", auto_run=True) 

    async def _plan_and_act(self, goal: str) -> Message:
        """
        The core loop: 
        1. Update plan based on goal
        2. Execute tasks one by one
        """
        # 1. Update Plan
        await self.planner.update_plan(goal=goal)
        
        results = []
        
        # 2. Loop through plan
        while self.planner.current_task:
            task = self.planner.current_task
            logger.info(f"Executing task: {task.instruction}")
            
            # HERE is where we would normally call other agents or tools
            # For now, we mock valid execution to verify the loop
            task_result_content = f"Executed {task.instruction}"
            task_result = self._create_task_result(task_result_content)
            
            # 3. Process Result (Update Plan/Memory)
            await self.planner.process_task_result(task_result)
            results.append(task_result_content)
            
        return Message(content="\n".join(results), role="assistant", cause_by=self.__class__)

    def _create_task_result(self, content: str):
        # Helper to create a TaskResult object expected by Planner
        from metagpt.schema import TaskResult
        return TaskResult(result=content, is_success=True)

    async def _act(self) -> Message:
        # Override _act to hijack the normal loop for planning
        # In a real scenario, this might be triggered by a specific message
        if not self.rc.history:
            return None
            
        last_msg = self.rc.history[-1]
        
        # Assume the last user message is the goal
        if last_msg.role == "user":
            return await self._plan_and_act(last_msg.content)
            
        return None
