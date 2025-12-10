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
    "scope-sentinel": "Scope Creep Detection, 'Just one quick thing', New Feature Requests, Unpaid Work Analysis",
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
    5. CRITICAL: Check the provided 'Context' for "Global Wisdom" or "Strategies". If a relevant strategy is found (e.g. from RAG_CONTEXT), you MUST explicitly instruct the assigned agent to use it by name.
    6. TIERED RAG: If a specific RAG document is relevant to a specific task, map its ID to 'rag_data_for_agent'.
    
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
                "instruction": "Detailed instruction (Mention Strategy Name if applicable)",
                "priority": "high",
                "rag_data_for_agent": "doc_id_or_summary",
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
    constraints: str = "Optimize for efficiency. MANDATORY: You must prioritize and apply 'Global Wisdom' strategies found in context."
    
    def __init__(self, **kwargs):
        super().__init__(actions=[CreatePlan()], **kwargs)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        """
        Direct entry point for generating a plan.
        Returns raw JSON string from the LLM.
        """
        # Prioritize RAG Context by placing it at the top
        ctx_parts = []
        if context and "RAG_CONTEXT" in context:
             ctx_parts.append(f"!!! GLOBAL WISDOM / RAG STRATEGIES !!!\n{context['RAG_CONTEXT']}\n!!! SYSTEM NOTE: USE THESE STRATEGIES !!!")
             # DEBUG Log
             logger.info("✅ RAG_CONTEXT Found and highlighted in Orchestrator arguments")
        elif context and "RAG_CONTEXT" not in context:
             logger.warning("❌ RAG_CONTEXT MISSING in Orchestrator arguments")
             
        for k, v in (context or {}).items():
             if k != "RAG_CONTEXT":
                  ctx_parts.append(f"{k}: {v}")
                  
        ctx_str = "\n\n".join(ctx_parts)
        
        # DEBUG: Log the context to verify RAG injection
        logger.info(f"🔍 ORCHESTRATOR INPUT CONTEXT: {ctx_str[:1000]}...")

        action = CreatePlan()
        
        # FORCE INSTRUCTION: Append system note to user request to override model bias
        forced_instruction = (
             f"{text}\n\n"
             "[SYSTEM NOTE: You MUST inspect the Context above for 'Global Wisdom' strategies (e.g. 'Escalation Strategy Beta'). "
             "If found, you MUST explicitly cite the strategy name in your plan instructions for the relevant agent.]"
        )
        
        return await action.run(instruction=forced_instruction, context=ctx_str)
