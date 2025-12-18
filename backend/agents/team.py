"""
FlagPilot Team - MetaGPT Team Orchestration
============================================
This module implements the team-based multi-agent collaboration
where agents can work autonomously and report back to each other.
"""

from typing import List, Dict, Any, Optional
import asyncio
from loguru import logger
from metagpt.team import Team
from metagpt.roles import Role
from metagpt.schema import Message
from agents.registry import registry

# Map readable IDs to module names
def _normalize_id(agent_id: str) -> str:
    return agent_id.replace("-", "_")

class FlagPilotTeam:
    """
    FlagPilot Multi-Agent Team
    
    Implements MGX.dev-style team orchestration where:
    1. FlagPilot orchestrator receives the task
    2. Orchestrator assigns sub-tasks to specialist agents
    3. Specialists execute and return results
    4. Orchestrator synthesizes the final answer
    """
    
    def __init__(self, agents: Optional[List[str]] = None):
        """
        Initialize the team with specified agents or all agents.
        
        Args:
            agents: List of agent IDs to include. None = all agents.
        """
        self.env = None
        self.agents = {}  # ID -> Role instance
        self.team = None
        self.agent_ids = agents
        
        # Initialize registry
        registry.initialize()
        
        # We need an orchestrator always? Or is it part of the agents list?
        # The original code had self.orchestrator = FlagPilotOrchestrator()
        # We should load it from registry dynamically too?
        # 'flagpilot' -> 'flagpilot_orchestrator'
        
        # Let's instantiate the orchestrator explicitly if we need strict access to it 
        # or load it as part of _init_team
        
        # We need orchestrator instance for self.orchestrator.analyze calls in run()
        orc_cls = registry.get_agent_class("flagpilot_orchestrator")
        if orc_cls:
            self.orchestrator = orc_cls()
        else:
            # Fallback if registry fails/missing
            logger.error("Orchestrator not found in registry!")
            from agents.roles.flagpilot_orchestrator import FlagPilotOrchestrator
            self.orchestrator = FlagPilotOrchestrator()

        self._init_team()
        
        # Initialize Standard MetaGPT Environment
        from metagpt.environment.base_env import Environment
        self.env = Environment()
        # Orchestrator also needs to be part of the environment?
        if self.orchestrator:
             self.env.add_role(self.orchestrator)

    def _init_team(self):
        """Initialize the MetaGPT Team with roles from Registry"""
        
        # If no agents specified, load ALL from registry (excluding orchestrator which is special)
        if not self.agent_ids:
            self.agent_ids = [
                name.replace("_", "-") 
                for name in registry.list_agents() 
                if name != "flagpilot_orchestrator"
            ]
        
        # Load requested agents
        self.active_agents = {} # Map ID -> Class (Wait, original code mapped ID -> Class, used in identify)
        # But we need INSTANCES for self.team.hire
        
        # Actually original code: self.active_agents = {id: RoleClass}
        # And run() did: agent = self.active_agents[agent_id]() -> New Instance per run
        # We should preserve that pattern.
        
        for agent_id in self.agent_ids:
            module_name = _normalize_id(agent_id)
            role_class = registry.get_agent_class(module_name)
            
            if role_class:
                self.active_agents[agent_id] = role_class
                # Also store an instance for tests/internal use
                self.agents[agent_id] = role_class()
                logger.debug(f"Loaded agent capability: {agent_id}")
            else:
                logger.warning(f"Agent {agent_id} not found in registry")
        
        # Also ensure we can hire them for the internal Team() if used
        # (Though current run implementation doesn't use self.team.run, it orchestrates manually)
        
        logger.info(f"FlagPilot Team initialized with {len(self.active_agents)} specialist capabilities")
    
    async def run(
        self, 
        task: str, 
        context: Optional[Dict[str, Any]] = None,
        n_round: int = 3
    ) -> Dict[str, Any]:
        """
        Run the team on a task with full orchestration.
        """
        logger.info(f"Starting team task: {task[:100]}...")
        
        # Build context string
        context_str = ""
        rag_context_str = ""
        if context:
            # RAG Context Injection
            user_id = context.get("id")
            if user_id:
                try:
                    from ragflow.client import get_ragflow_client
                    from lib.memory.manager import memory_manager
                    
                    client = get_ragflow_client()
                    
                    # 1. Get Personal Memory (Dynamic Profile)
                    user_summary = await memory_manager.get_current_user_profile(user_id)
                    if user_summary:
                        logger.info(f"Retrieved personal memory for user {user_id}")
                        context["USER_MEMORY"] = user_summary
                    
                    # 2. Get Shared Memory (Similar Experiences)
                    similar_lessons = await memory_manager.search_similar_experiences(task, limit=2)
                    if similar_lessons:
                        lessons_text = "\n".join([f"- {l['lesson']}" for l in similar_lessons])
                        logger.info(f"Retrieved {len(similar_lessons)} shared lessons.")
                        context["SHARED_WISDOM"] = lessons_text

                    # 3. Get Vault Context (RAGFlow)
                    results = await client.search_user_context(user_id, task, limit=5)
                    rag_context_str = "\n\n".join([f"Context [{r['similarity']:.2f}]: {r['content']}" for r in results])
                    
                    if rag_context_str:
                        logger.info(f"Injected RAG context ({len(results)} chunks) for user {user_id}")
                        context["RAG_CONTEXT"] = rag_context_str
                except Exception as e:
                    logger.warning(f"Failed to inject RAG context/memory: {e}")

            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
        
        results = {
            "task": task,
            "context": context,
            "orchestrator_analysis": None,
            "agent_outputs": {},
            "final_synthesis": None,
        }
        
        try:
            # Step 1: Orchestrator analyzes and plans
            logger.info("Step 1: Orchestrator analyzing task...")
            # We must ensure Orchestrator has the RAG context too!
            plan_str = await self.orchestrator.analyze(task, context)
            
            # PARSE PLAN JSON SAFEGUARD
            import json
            try:
                plan = json.loads(plan_str)
            except json.JSONDecodeError:
                # Fallback if valid JSON isn't returned, treat as raw plan text
                logger.warning("Orchestrator output is not valid JSON. Using fallback logic.")
                plan = {"outcome": "plan", "nodes": [], "raw": plan_str}

            results["orchestrator_analysis"] = plan
            
            outcome = plan.get("outcome")

            # --- 🛡️ EXPANDED FAST-FAIL & SMART ORCHESTRATION ---
            
            # Case A: Happy Path Short-Circuit (Direct Response)
            if outcome == "direct_response":
                logger.info("⚡ Smart Orchestration: Direct Response bypass.")
                direct_content = plan.get("direct_response_content", "No content provided.")
                return {
                    "task": task,
                    "context": context,
                    "orchestrator_analysis": plan,
                    "agent_outputs": {},
                    "final_synthesis": direct_content,
                    "status": "COMPLETED_DIRECT"
                }

            # Case B: Security/Safety Abort
            if outcome == "interrupted":
                logger.warning("⛔ Fast-Fail: Workflow Interrupted by Orchestrator")
                return {
                    "task": task,
                    "context": context,
                    "orchestrator_analysis": plan,
                    "agent_outputs": {},
                    "final_synthesis": "I cannot fulfill this request. The Orchestrator has interrupted the process due to safety, security, or context violations.",
                    "status": "BLOCKED",
                    "risk_level": "CRITICAL"
                }
                
            # Case C: Ambiguity Trap
            if outcome == "clarification_needed":
                return {
                    "task": task,
                    "context": context,
                    "orchestrator_analysis": plan,
                    "agent_outputs": {},
                    "final_synthesis": f"I need clarification: {plan.get('clarification_question')}",
                    "status": "WAITING_FOR_USER"
                }
                
            # Case D: Single Agent Fast-Path
            # If implementation supports it, we could check if only 1 node is in the plan
            # and it's a "simple" task, we might skip complex synthesis?
            # For now, we continue to Step 2.
            # ---------------------------------------------
            
            # Step 2: Identify relevant agents based on task
            relevant_agents = self._identify_relevant_agents(task)
            logger.info(f"Step 2: Relevant agents identified: {relevant_agents}")
            
            # Step 3: Run relevant agents in parallel
            logger.info("Step 3: Running specialist agents...")
            agent_tasks = []
            for agent_id in relevant_agents:
                if agent_id in self.active_agents:
                    # Instantiate fresh agent for the task
                    agent_cls = self.active_agents[agent_id]
                    
                    agent = agent_cls() 
                    
                    # Add agent to environment for message exchange capability
                    if self.env:
                        # Update environment context with the request context
                        if context:
                            for k, v in context.items():
                                self.env.context.kwargs.set(k, v)
                        self.env.add_role(agent)
                    elif context:
                        # Fallback if no env
                         from metagpt.context import Context
                         ctx = Context()
                         for k, v in context.items():
                             ctx.kwargs.set(k, v)
                         agent.context = ctx
                    
                    agent_tasks.append(self._run_agent(agent_id, agent, task, context))
            
            if agent_tasks:
                agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
                
                # --- FEATURE: RISK AGGREGATOR ---
                critical_risks = []
                # --------------------------------
                
                for agent_id, result in zip(relevant_agents, agent_results):
                    if isinstance(result, Exception):
                        results["agent_outputs"][agent_id] = f"Error: {str(result)}"
                    else:
                        results["agent_outputs"][agent_id] = result
                        
                        # Check for CRITICAL RISK signals in JSON-like agent output
                        # We try to parse agent output if it looks like JSON, or check for specific keywords
                        try:
                            result_str = str(result).lower()
                            # Heuristic: Check if output contains "is_critical_risk": true
                            if '"is_critical_risk": true' in result_str or "'is_critical_risk': true" in result_str:
                                critical_risks.append(f"CRITICAL RISK detected by {agent_id}")
                                logger.warning(f"🚨 CRITICAL RISK SIGNAL received from {agent_id}")
                            
                            # Additional Safety Net: Regex for strong scam warnings
                            if "scam detected" in result_str or "fraud alert" in result_str:
                                critical_risks.append(f"SCAM WARNING from {agent_id}")
                                
                        except Exception:
                            pass

                # If Critical Risks detected, Force Abort/Synthesis on risks
                if critical_risks:
                    logger.warning("🚨 ABORTING MISSION: Critical Risks Detected.")
                    abort_message = f"**MISSION ABORTED DUE TO CRITICAL RISKS**\n\n{'; '.join(critical_risks)}\n\nPlease review the warnings above immediately. Do not proceed."
                    results["final_synthesis"] = abort_message
                    results["status"] = "ABORTED_ON_RISK"
                    return results
                # --------------------------------
            
            # Step 4: Synthesize results
            logger.info("Step 4: Synthesizing results...")
            results["final_synthesis"] = await self._synthesize_results(
                task, results["orchestrator_analysis"], results["agent_outputs"]
            )
            
            # Step 5: Update User Memory (Async background)
            if user_id:
                try:
                    from lib.memory.manager import memory_manager
                    interaction_summary = f"Task: {task}\nResult: {results['final_synthesis']}"
                    # Use create_task to avoid blocking the main response
                    asyncio.create_task(
                        memory_manager.summarize_and_update(user_id, context.get("USER_MEMORY", ""), interaction_summary)
                    )
                except Exception as e:
                    logger.warning(f"Failed to trigger memory update: {e}")

        except Exception as e:
            logger.error(f"Team execution error: {e}")
            results["error"] = str(e)
        
        return results
    
    async def _run_agent(
        self, 
        agent_id: str, 
        agent: Role, 
        task: str, 
        context: Optional[Dict]
    ) -> str:
        """Run a single agent on the task"""
        try:
            result = await agent.analyze(task, context)
            return result
        except Exception as e:
            logger.error(f"Agent {agent_id} error: {e}")
            return f"Error: {str(e)}"
    
    def _identify_relevant_agents(self, task: str) -> List[str]:
        """Identify which agents should work on this task"""
        task_lower = task.lower()
        relevant = []
        
        # Contract-related
        if any(w in task_lower for w in ["contract", "agreement", "terms", "clause", "sign"]):
            relevant.append("contract-guardian")
        
        # Job-related
        if any(w in task_lower for w in ["job", "posting", "scam", "fake", "opportunity", "position"]):
            relevant.append("job-authenticator")
        
        # Payment-related
        if any(w in task_lower for w in ["payment", "invoice", "overdue", "collect", "owe", "pay"]):
            relevant.append("payment-enforcer")
        
        # Talent/hiring-related
        if any(w in task_lower for w in ["candidate", "freelancer", "hire", "portfolio", "evaluate", "resume", "cv", "experience"]):
            relevant.append("talent-vet")
        
        # Ghosting-related
        if any(w in task_lower for w in ["ghost", "silent", "respond", "follow up", "no response"]):
            relevant.append("ghosting-shield")
        
        # Scope-related
        if any(w in task_lower for w in ["scope", "creep", "additional", "extra", "change request", "benchmark"]):
            relevant.append("scope-sentinel")
        
        # Dispute-related
        if any(w in task_lower for w in ["dispute", "conflict", "disagree", "problem", "issue"]):
            relevant.append("dispute-mediator")
        
        # Profile-related
        if any(w in task_lower for w in ["profile", "bio", "summary", "headline", "optimize"]):
            relevant.append("profile-analyzer")
        
        # Communication-related
        if any(w in task_lower for w in ["message", "email", "write", "draft", "communicate", "proposal"]):
            relevant.append("communication-coach")
        
        # Negotiation-related
        if any(w in task_lower for w in ["rate", "salary", "negotiate", "price", "cost", "budget", "benchmark"]):
            relevant.append("negotiation-assistant")
        
        # Application-related
        if any(w in task_lower for w in ["application", "applicant", "spam", "ai generated", "screen"]):
            relevant.append("application-filter")
        
        # If no specific agents identified, use a broad set
        if not relevant:
            relevant = ["profile-analyzer", "communication-coach", "job-authenticator"]
        
        return relevant
    
    async def _synthesize_results(
        self, 
        task: str, 
        plan: str, 
        agent_outputs: Dict[str, str]
    ) -> str:
        """Synthesize all agent outputs into a final response"""
        outputs_str = "\n\n".join([
            f"**{agent_id}**:\n{output}" 
            for agent_id, output in agent_outputs.items()
        ])
        
        synthesis_prompt = f"""
Based on the following agent analyses, provide a comprehensive final response.

Original Task: {task}

Orchestrator Plan:
{plan}

Agent Outputs:
{outputs_str}

Synthesize these into:
1. KEY FINDINGS - Most important discoveries
2. RECOMMENDED ACTIONS - Prioritized next steps
3. WARNINGS - Any risks or concerns
4. RESOURCES - Templates, scripts, or tools provided

Be comprehensive but actionable.
"""
        
        # Use orchestrator to synthesize
        from metagpt.actions import Action
        action = Action(name="Synthesize")
        return await action._aask(synthesis_prompt)


async def run_team_task(
    task: str,
    context: Optional[Dict[str, Any]] = None,
    agents: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to run a team task.
    
    Args:
        task: The task to complete
        context: Additional context
        agents: Specific agents to use (None = all)
    
    Returns:
        Team execution results
    """
    team = FlagPilotTeam(agents=agents)
    return await team.run(task, context)
