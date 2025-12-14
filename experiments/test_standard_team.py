"""
Experiment: Standard MetaGPT Team Pattern with FlagPilot Agents
===============================================================
This script verifies that we can use the standard `metagpt.team.Team` 
and `metagpt.context.Context` with our custom FlagPilot agents.

Goal:
1. Initialize a generic MetaGPT Team.
2. Inject User ID via standard Context.
3. Hire FlagPilot agents (ContractGuardian).
4. Run a task and verify context propagation.
"""

import asyncio
import sys
import os

# Add backend to path so we can import agents
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from metagpt.team import Team
from metagpt.context import Context
from metagpt.environment import Environment
from metagpt.logs import logger

# Import our custom agent
from agents.roles.contract_guardian import ContractGuardian

async def main():
    logger.info("🧪 Starting Standard Team Experiment")

    # 1. Create Standard Context
    # We use kwargs to store our custom user_id, which is flexible
    ctx = Context()
    ctx.kwargs["user_id"] = "test-user-123"
    ctx.kwargs["session_id"] = "session-abc"
    
    logger.info(f"✅ Context created with user_id: {ctx.kwargs['user_id']}")

    # 2. Initialize Standard Team
    # We pass the context here. In standard MetaGPT, Team initializes its own Environment with this context.
    team = Team(context=ctx)
    team.max_round = 2 # Short run for testing
    
    # 3. Hire Agents
    # We instantiate the role. Note: We don't pass context here manually anymore!
    # The Role should pick it up from the Team's Environment or setter.
    guardian = ContractGuardian()
    team.hire([guardian])
    
    logger.info("✅ Hired ContractGuardian")

    # 4. Run Project
    task_description = "Analyze this NDA: Non-compete for 10 years worldwide."
    
    # Note: users of standard Team often use run_project or run directly
    logger.info(f"🚀 Running task: {task_description}")
    
    # Run the team
    # Ideally, ContractGuardian should access `self.context.kwargs['user_id']` inside its run/analyze method
    # But wait, we previously patched `FlagPilotAction.run` to accept `runtime_context`.
    # Standard Roles use `self.context`. We need to verify if `FlagPilotRole` bridges this.
    
    history = await team.run(idea=task_description, n_round=1)
    
    logger.info("🏁 Team Run Complete")
    print(history)

if __name__ == "__main__":
    asyncio.run(main())
