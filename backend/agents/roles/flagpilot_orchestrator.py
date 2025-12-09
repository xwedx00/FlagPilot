"""
FlagPilot Orchestrator - Main Agent that coordinates the team
"""

import json
from typing import ClassVar, List, Dict, Any, Optional

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from loguru import logger

# Context for the Orchestrator to know about its team
AGENT_CAPABILITIES = {
    "contract-guardian": "Contract Analysis, Legal Risk Assessment, Clause Review",
    "job-authenticator": "Scam Detection, Job Verification, Company Legitimacy Check",
    "profile-analyzer": "Client Research, Company Profiling, LinkedIn Analysis",
    "communication-coach": "Email Drafting, Professional Communication, Anti-Ghosting",
    "negotiation-assistant": "Rate Negotiation, Deal Strategy, Compensation Analysis",
    "talent-vet": "Resume Review, Portfolio Analysis, Skill Assessment",
    "dispute-mediator": "Conflict Resolution, Evidence Analysis, Mediation",
    "payment-enforcer": "Invoice Collection, Payment Tracking, Financial Protection",
    "scope-sentinel": "Scope Creep Detection, Change Order Management",
    "ghosting-shield": "Re-engagement Strategies, Follow-up Planning",
    "application-filter": "Spam Detection, Applicant Screening, Quality Filtering",
    "feedback-loop": "Feedback Analysis, Continuous Improvement",
}

class CreatePlan(FlagPilotAction):
    """Create a comprehensive workflow plan in JSON format"""
    name: str = "CreatePlan"
    desc: str = "Analyze the request and create a detailed execution plan."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are FlagPilot Orchestrator, the master planner of a multi-agent system.
    
    Available Specialist Agents:
    {agents}
    
    User Request:
    {request}
    
    Context:
    {context}
    
    Task:
    1. Analyze the user's complex request.
    2. Break it down into atomic, logical tasks.
    3. Assign the BEST specialist agent for each task.
    4. Determine dependencies (which task must finish before another starts).
    
    Output strictly in VALID JSON format.
    Do not include any thinking chain, markdown formatting, or introductory text.
    The response should start with {{ and end with }}.
    
    JSON Schema:
    {{
        "objective": "Brief summary",
        "nodes": [
            {{
                "id": "task-1",
                "agent": "agent-id",
                "instruction": "Detailed instruction",
                "priority": "high",
                "dependencies": []
            }}
        ]
    }}
    """
    
    async def run(self, instruction: str, context: str = "") -> str:
        agents_str = "\n".join([f"- {k}: {v}" for k,v in AGENT_CAPABILITIES.items()])
        
        prompt = self.PROMPT_TEMPLATE.format(
            agents=agents_str,
            request=instruction,
            context=context
        )
        
        # Use centralized LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)


class FlagPilotOrchestrator(FlagPilotRole):
    """
    FlagPilot Orchestrator Role
    Decides 'Who does what' and 'In what order' to solve user problems.
    """
    
    name: str = "FlagPilotOrchestrator"
    profile: str = "Workflow Manager"
    goal: str = "Orchestrate the perfect team for any freelancer problem"
    constraints: str = "Optimize for efficiency and accuracy. Use RAG context where available."
    
    def __init__(self, **kwargs):
        super().__init__(actions=[CreatePlan()], **kwargs)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        """
        Direct entry point for generating a plan.
        Returns raw JSON string from the LLM.
        """
        action = CreatePlan()
        ctx_str = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await action.run(instruction=text, context=ctx_str)
