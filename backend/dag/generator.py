"""
Dynamic DAG Generator

Uses LLM to decompose user requests into a workflow DAG.
The generated DAG can be executed by DAGExecutor.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger

from .schemas import WorkflowPlan, TaskNode, TaskPriority


# Agent capabilities for task routing
AGENT_CAPABILITIES = {
    "contract-guardian": {
        "name": "Contract Guardian",
        "keywords": ["contract", "agreement", "clause", "legal", "terms", "liability", "indemnification"],
        "description": "Contract analysis, clause review, risk assessment"
    },
    "profile-analyzer": {
        "name": "Profile Analyzer",
        "keywords": ["research", "client", "company", "background", "linkedin", "crunchbase", "profile", "reputation"],
        "description": "Deep web research, client background checks, company profiles"
    },
    "negotiation-assistant": {
        "name": "Negotiation Assistant",
        "keywords": ["rate", "salary", "negotiate", "price", "budget", "cost", "deal", "offer", "compensation"],
        "description": "Rate negotiation, deal strategy, pricing tactics"
    },
    "payment-enforcer": {
        "name": "Payment Enforcer",
        "keywords": ["payment", "invoice", "overdue", "collect", "pay", "chase", "late", "tax", "financial"],
        "description": "Payment collection, invoice management, financial tracking"
    },
    "scope-sentinel": {
        "name": "Scope Sentinel",
        "keywords": ["scope", "creep", "change", "additional", "extra", "boundary", "sow", "privacy", "security"],
        "description": "Scope creep detection, change order management, privacy protection"
    },
    "dispute-mediator": {
        "name": "Dispute Mediator",
        "keywords": ["dispute", "conflict", "mediate", "resolve", "evidence", "claim"],
        "description": "Dispute resolution, evidence collection, mediation"
    },
    "talent-vet": {
        "name": "Talent Vet",
        "keywords": ["resume", "portfolio", "skills", "career", "optimize", "improve", "vetting"],
        "description": "Profile optimization, skill development, career advice"
    },
    "communication-coach": {
        "name": "Communication Coach",
        "keywords": ["email", "message", "draft", "communicate", "followup", "write", "ghosting"],
        "description": "Email drafting, professional communication, anti-ghosting"
    },
    "job-authenticator": {
        "name": "Job Authenticator",
        "keywords": ["job", "posting", "scam", "fake", "legitimate", "verify", "authentic"],
        "description": "Job posting verification, scam detection"
    },
    "feedback-loop": {
        "name": "Feedback Loop",
        "keywords": ["deadline", "milestone", "project", "track", "status", "progress", "feedback"],
        "description": "Project tracking, deadline management, continuous feedback"
    },
}


PLANNER_SYSTEM_PROMPT = """You are FlagPilot, the Chief Orchestrator for a freelancer protection platform.

Your job is to break down user requests into a workflow of tasks that specialist agents will execute.

Available Agents:
{agent_list}

Rules:
1. Break complex requests into atomic, focused tasks
2. Identify dependencies between tasks (what must finish before another starts)
3. Enable parallelism where possible (tasks with no dependencies can run together)
4. Assign the most appropriate agent to each task based on their specialization
5. Keep task instructions specific and actionable
6. Include a maximum of 5 tasks for simple requests, up to 8 for complex ones

OUTPUT: Return ONLY valid JSON matching this schema (no markdown, no explanation):
{{
    "objective": "Brief description of what we're accomplishing",
    "nodes": [
        {{
            "id": "task-1",
            "agent": "agent-id from the list",
            "instruction": "Specific task description",
            "dependencies": [],
            "priority": "critical|high|medium|low"
        }},
        {{
            "id": "task-2", 
            "agent": "another-agent-id",
            "instruction": "Another task that depends on task-1",
            "dependencies": ["task-1"],
            "priority": "high"
        }}
    ]
}}
"""


def _identify_relevant_agents(task: str) -> List[str]:
    """Identify which agents are relevant to a task based on keywords"""
    task_lower = task.lower()
    relevant = []
    
    for agent_id, info in AGENT_CAPABILITIES.items():
        if any(kw in task_lower for kw in info["keywords"]):
            relevant.append(agent_id)
    
    return relevant


def _build_agent_list() -> str:
    """Build formatted agent list for the prompt"""
    lines = []
    for agent_id, info in AGENT_CAPABILITIES.items():
        lines.append(f"- {agent_id}: {info['description']}")
    return "\n".join(lines)


async def generate_workflow_plan(
    user_request: str,
    context: Optional[Dict[str, Any]] = None,
    available_agents: Optional[List[str]] = None,
) -> WorkflowPlan:
    """
    Generate a dynamic workflow DAG from a user request.
    
    Uses LLM to decompose the request into tasks and dependencies.
    Falls back to simple plan if LLM fails.
    
    Args:
        user_request: The user's natural language request
        context: Additional context (user info, uploaded files, etc.)
        available_agents: Limit to specific agents (None = all)
    
    Returns:
        WorkflowPlan ready for execution
    """
    workflow_id = f"workflow-{uuid.uuid4().hex[:8]}"
    
    # Build prompt
    agent_list = _build_agent_list()
    system_prompt = PLANNER_SYSTEM_PROMPT.format(agent_list=agent_list)
    
    user_prompt = f"User Request: {user_request}"
    if context:
        user_prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"
    
    try:
        # Try to use LLM for planning
        plan_data = await _call_llm_for_plan(system_prompt, user_prompt)
        
        # Validate and filter agents if needed
        if available_agents:
            plan_data["nodes"] = [
                n for n in plan_data["nodes"] 
                if n["agent"] in available_agents
            ]
        
        # Build WorkflowPlan
        nodes = []
        for node_data in plan_data.get("nodes", []):
            nodes.append(TaskNode(
                id=node_data["id"],
                agent=node_data["agent"],
                instruction=node_data["instruction"],
                dependencies=node_data.get("dependencies", []),
                priority=TaskPriority(node_data.get("priority", "medium")),
            ))
        
        plan = WorkflowPlan(
            id=workflow_id,
            objective=plan_data.get("objective", user_request[:100]),
            nodes=nodes,
        )
        
        logger.info(f"Generated workflow {workflow_id} with {len(nodes)} tasks")
        return plan
        
    except Exception as e:
        logger.warning(f"LLM planning failed, using fallback: {e}")
        return _create_fallback_plan(workflow_id, user_request, available_agents)


async def _call_llm_for_plan(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Call LLM to generate the plan using MetaGPT Action.
    
    This ensures ALL LLM calls go through MetaGPT's managed infrastructure,
    not direct openai/openrouter calls.
    """
    from metagpt.actions import Action
    
    # Create a planning action
    class PlanningAction(Action):
        """Action for generating workflow plans"""
        name: str = "GenerateWorkflowPlan"
    
    action = PlanningAction()
    
    # Combine prompts for the action
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    try:
        # Use MetaGPT's _aask which goes through configured LLM
        response = await action._aask(full_prompt)
        
        # Extract JSON from response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        
        if json_start >= 0 and json_end > json_start:
            return json.loads(response[json_start:json_end])
        
        raise ValueError("No valid JSON in LLM response")
        
    except Exception as e:
        logger.error(f"MetaGPT planning action failed: {e}")
        raise


def _create_fallback_plan(
    workflow_id: str, 
    user_request: str,
    available_agents: Optional[List[str]] = None
) -> WorkflowPlan:
    """
    Create a heuristic-based fallback plan when LLM fails.
    Detects intent (Contract vs Resume) and assigns specific focused tasks.
    """
    nodes = []
    
    # Heuristic 1: Contract Analysis
    if "contract" in user_request.lower() or "agreement" in user_request.lower():
        nodes.append(TaskNode(
            id="task-contract",
            agent="contract-guardian",
            instruction="Focus ONLY on analyzing the contract/agreement documents. Identify risks, non-competes, IP rights, and salary effectiveness sentences.",
            priority=TaskPriority.CRITICAL,
            dependencies=[]
        ))

    # Heuristic 2: Resume/Candidate Ranking
    if "resume" in user_request.lower() or "candidate" in user_request.lower() or "hiring" in user_request.lower():
        nodes.append(TaskNode(
            id="task-ranking",
            agent="talent-vet" if not available_agents or "talent-vet" in available_agents else "contract-guardian",
            instruction="Focus ONLY on analyzing the candidates/resumes. Rank them against the Job Description capabilities and experience requirements.",
            priority=TaskPriority.HIGH,
            dependencies=[]
        ))
    
    # Heuristic 3: Negotiation/Mediation (if complex)
    if len(nodes) > 1:
        # If we have both, add a synthesis step
        nodes.append(TaskNode(
            id="task-synthesis",
            agent="dispute-mediator",
            instruction="Synthesize the findings from the Contract Analysis and Candidate Ranking. Propose a final strategy.",
            priority=TaskPriority.MEDIUM,
            dependencies=["task-contract", "task-ranking"]
        ))
    
    # Fallback if no specific keywords matched (Generic)
    if not nodes:
        relevant_agents = _identify_relevant_agents(user_request)
        if available_agents:
            relevant_agents = [a for a in relevant_agents if a in available_agents]
        if not relevant_agents:
            relevant_agents = ["contract-guardian"] # Default to guardian
            
        for i, agent_id in enumerate(relevant_agents[:2]):
            nodes.append(TaskNode(
                id=f"task-{i+1}",
                agent=agent_id,
                instruction=f"Analyze and assist with: {user_request}",
                dependencies=[] if i == 0 else [f"task-{i}"],
                priority=TaskPriority.HIGH if i == 0 else TaskPriority.MEDIUM,
            ))

    return WorkflowPlan(
        id=workflow_id,
        objective=user_request[:100],
        nodes=nodes,
    )
