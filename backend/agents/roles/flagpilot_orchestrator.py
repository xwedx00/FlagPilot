"""
FlagPilot Orchestrator - Main Agent that coordinates the team
This is the 13th agent that orchestrates all 12 specialists
"""

import os
from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from metagpt.llm import LLM
from metagpt.config2 import Config
from typing import ClassVar, List
from loguru import logger

# Import centralized LLM configuration
from config import get_configured_llm


class OrchestrateTask(Action):
    """Orchestrate tasks across specialist agents"""
    
    name: str = "OrchestrateTask"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are FlagPilot, the main orchestrator of a 12-agent team helping freelancers and HR professionals.

Your specialist agents:
1. ContractGuardian - Contract analysis and risk detection
2. JobAuthenticator - Scam detection and job verification
3. PaymentEnforcer - Payment collection strategies
4. TalentVet - Freelancer profile evaluation
5. GhostingShield - Follow-up strategies
6. ScopeSentinel - Scope creep detection
7. DisputeMediator - Conflict resolution
8. ProfileAnalyzer - Profile optimization
9. CommunicationCoach - Message improvement
10. NegotiationAssistant - Rate negotiation
11. ApplicationFilter - Spam/AI detection
12. FeedbackLoop - Feedback processing

User's request:
{content}

Context (user info, goals, data provided):
{context}

Your task:
1. UNDERSTAND the user's needs
2. IDENTIFY which specialists should be involved
3. CREATE A PLAN of tasks for each specialist
4. COORDINATE their work
5. SYNTHESIZE their outputs into a comprehensive response

Provide:
- ANALYSIS of what needs to be done
- TASK DELEGATION plan (which agents handle what)
- EXPECTED OUTPUTS from each agent
- INTEGRATION strategy for combining results
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        # Use our configured LLM instead of relying on context
        llm = get_configured_llm()
        return await llm.aask(prompt)



class FlagPilotOrchestrator(Role):
    """FlagPilot Orchestrator - Coordinates all specialist agents"""
    
    name: str = "FlagPilot"
    profile: str = "Multi-Agent Orchestrator"
    goal: str = "Coordinate specialist agents to provide comprehensive freelancer assistance"
    constraints: str = "Use the right specialists, synthesize outputs, be comprehensive"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([OrchestrateTask])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        """Direct orchestration for API calls"""
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await OrchestrateTask().run(content=text, context=ctx)
    
    async def orchestrate(self, task: str, user_data: dict = None) -> dict:
        """
        Full orchestration with actual agent delegation.
        
        1. Query Global Wisdom for similar successful workflows
        2. Use suggestions to inform agent selection
        3. Run relevant agents
        4. Return combined results
        """
        from .contract_guardian import ContractGuardian
        from .job_authenticator import JobAuthenticator
        from .payment_enforcer import PaymentEnforcer
        from .profile_analyzer import ProfileAnalyzer
        from .communication_coach import CommunicationCoach
        
        results = {
            "orchestrator_plan": await self.analyze(task, user_data),
            "agent_outputs": {},
            "global_wisdom_suggestions": []
        }
        
        # Query Global Wisdom for similar successful workflows
        # Query Ragflow for (Global Wisdom + Personal Context)
        try:
            from ragflow import get_ragflow_client
            
            client = get_ragflow_client()
            
            # Fetch aggregated context (Global Patterns + User Data)
            # This is "Assistant to MetaGPT" mode - fetching context to inform the plan
            rag_context = await client.get_agent_context(
                user_id=user_data.get("id", "anonymous") if user_data else "anonymous",
                query=task
            )
            
            if rag_context:
                results["orchestrator_plan"] += f"\n\n=== RAG Context ===\n{rag_context}\n==================="
                results["global_wisdom_suggestions"] = [{"content": "Context injected into plan"}]
                    
        except Exception as e:
            # Continue without Global Wisdom if not available
            logger.warning(f"RAG context retrieval failed: {e}")
            pass
        
        # Based on task and Global Wisdom, delegate to relevant agents
        task_lower = task.lower()
        
        if "contract" in task_lower or "agreement" in task_lower:
            agent = ContractGuardian()
            results["agent_outputs"]["contract_guardian"] = await agent.analyze(task, user_data)
        
        if "job" in task_lower or "posting" in task_lower or "scam" in task_lower:
            agent = JobAuthenticator()
            results["agent_outputs"]["job_authenticator"] = await agent.analyze(task, user_data)
        
        if "payment" in task_lower or "invoice" in task_lower or "overdue" in task_lower:
            agent = PaymentEnforcer()
            results["agent_outputs"]["payment_enforcer"] = await agent.analyze(task, user_data)
        
        if "profile" in task_lower or "portfolio" in task_lower:
            agent = ProfileAnalyzer()
            results["agent_outputs"]["profile_analyzer"] = await agent.analyze(task, user_data)
        
        if "message" in task_lower or "email" in task_lower or "communication" in task_lower:
            agent = CommunicationCoach()
            results["agent_outputs"]["communication_coach"] = await agent.analyze(task, user_data)
        
        return results

