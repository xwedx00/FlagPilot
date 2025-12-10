"""
Dynamic DAG Generator using MetaGPT Orchestrator Role
"""

import json
import uuid
from typing import Dict, Any, Optional, List
from loguru import logger

from .schemas import WorkflowPlan, TaskNode, TaskPriority

# Import the unified Orchestrator Role
from agents.roles.flagpilot_orchestrator import FlagPilotOrchestrator

async def generate_workflow_plan(
    user_request: str,
    context: Optional[Dict[str, Any]] = None,
    available_agents: Optional[List[str]] = None,
) -> WorkflowPlan:
    """
    Generate workflow using the Orchestrator Role.
    """
    workflow_id = f"workflow-{uuid.uuid4().hex[:8]}"
    plan_json_str = "Not Generated"
    
    try:
        # Instantiate orchestrator
        orchestrator = FlagPilotOrchestrator()
        
        # Run analysis (generates JSON plan)
        plan_json_str = await orchestrator.analyze(
            user_request, 
            context={"available_agents": available_agents} if available_agents else context
        )
        
        # Parse JSON output (Handle potential markdown blocks from LLM)
        clean_json = plan_json_str
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0]
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0]
            
        clean_json = clean_json.strip()
        
        try:
            plan_data = json.loads(clean_json)
        except json.JSONDecodeError:
            # Fallback: try to find strict JSON bounds
            json_start = clean_json.find("{")
            json_end = clean_json.rfind("}") + 1
            if json_start != -1 and json_end != -1:
                plan_data = json.loads(clean_json[json_start:json_end])
            else:
                raise
        
        nodes = []
        for node_data in plan_data.get("nodes", []):
            agent_id = node_data["agent"]
            
            nodes.append(TaskNode(
                id=node_data.get("id", uuid.uuid4().hex[:6]),
                agent=agent_id,
                instruction=node_data["instruction"],
                dependencies=node_data.get("dependencies", []),
                priority=TaskPriority(node_data.get("priority", "medium")),
            ))
            
        return WorkflowPlan(
            id=workflow_id,
            objective=plan_data.get("objective", user_request[:100]),
            outcome=plan_data.get("outcome", "plan"),
            direct_response_content=plan_data.get("direct_response_content"),
            nodes=nodes
        )
        
    except Exception as e:
        logger.error(f"Orchestrator planning failed: {e}")
        logger.error(f"Failed JSON Content: {plan_json_str}")
        # Fallback to simple single-node plan
        return WorkflowPlan(
            id=workflow_id,
            objective=user_request[:100],
            nodes=[
                TaskNode(
                    id="fallback-task",
                    agent="flagpilot", # Safe default
                    instruction=f"Process request due to planning error: {user_request}",
                    priority=TaskPriority.HIGH
                )
            ]
        )
