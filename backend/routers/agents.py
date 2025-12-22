"""
FlagPilot Agents Router
=======================
Provides agent metadata endpoints.
MetaGPT agents run in isolated environment via CopilotKit -> LangGraph -> MetaGPTRunner.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from loguru import logger

router = APIRouter(prefix="/api", tags=["Agents"])

# Static agent metadata (MetaGPT is in isolated venv)
AGENTS = {
    "contract-guardian": {
        "id": "contract-guardian",
        "name": "Contract Guardian",
        "description": "Analyzes legal contracts for risks and unfair clauses",
        "profile": "Senior Legal AI Analyst",
        "goal": "Protect freelancers from unfair contracts"
    },
    "job-authenticator": {
        "id": "job-authenticator",
        "name": "Job Authenticator",
        "description": "Verifies job postings and detects scams",
        "profile": "Job Verification Specialist",
        "goal": "Identify fraudulent job postings"
    },
    "scope-sentinel": {
        "id": "scope-sentinel",
        "name": "Scope Sentinel",
        "description": "Detects scope creep and project boundary violations",
        "profile": "Project Scope Analyst",
        "goal": "Prevent unauthorized scope expansion"
    },
    "payment-enforcer": {
        "id": "payment-enforcer",
        "name": "Payment Enforcer",
        "description": "Tracks payments and creates collection strategies",
        "profile": "Payment Recovery Specialist",
        "goal": "Ensure freelancers get paid"
    },
    "dispute-mediator": {
        "id": "dispute-mediator",
        "name": "Dispute Mediator",
        "description": "Mediates conflicts between freelancers and clients",
        "profile": "Conflict Resolution Expert",
        "goal": "Resolve disputes fairly"
    },
    "communication-coach": {
        "id": "communication-coach",
        "name": "Communication Coach",
        "description": "Helps craft professional messages and proposals",
        "profile": "Professional Communication Expert",
        "goal": "Improve client communication"
    },
    "negotiation-assistant": {
        "id": "negotiation-assistant",
        "name": "Negotiation Assistant",
        "description": "Provides rate negotiation strategies and benchmarks",
        "profile": "Rate Negotiation Specialist",
        "goal": "Help freelancers negotiate fair rates"
    },
    "profile-analyzer": {
        "id": "profile-analyzer",
        "name": "Profile Analyzer",
        "description": "Analyzes and optimizes freelancer profiles",
        "profile": "Profile Optimization Expert",
        "goal": "Maximize profile effectiveness"
    },
    "ghosting-shield": {
        "id": "ghosting-shield",
        "name": "Ghosting Shield",
        "description": "Detects client ghosting patterns and provides recovery",
        "profile": "Client Engagement Specialist",
        "goal": "Prevent and recover from ghosting"
    },
    "risk-advisor": {
        "id": "risk-advisor",
        "name": "Risk Advisor",
        "description": "Provides overall risk assessment and mitigation",
        "profile": "Risk Management Consultant",
        "goal": "Minimize freelancer business risks"
    },
    "talent-vet": {
        "id": "talent-vet",
        "name": "Talent Vet",
        "description": "Evaluates candidates and team members",
        "profile": "Talent Assessment Specialist",
        "goal": "Help identify quality collaborators"
    },
    "application-filter": {
        "id": "application-filter",
        "name": "Application Filter",
        "description": "Filters and prioritizes job applications",
        "profile": "Application Screening Expert",
        "goal": "Identify best opportunities"
    },
    "feedback-loop": {
        "id": "feedback-loop",
        "name": "Feedback Loop",
        "description": "Learns from user interactions and improves",
        "profile": "Continuous Improvement Analyst",
        "goal": "Enhance system effectiveness"
    },
    "planner-role": {
        "id": "planner-role",
        "name": "Planner Role",
        "description": "Plans and organizes complex workflows",
        "profile": "Strategic Planner",
        "goal": "Optimize workflow execution"
    },
    "flagpilot-orchestrator": {
        "id": "flagpilot-orchestrator",
        "name": "FlagPilot Orchestrator",
        "description": "Coordinates all agents for complex tasks",
        "profile": "Multi-Agent Coordinator",
        "goal": "Orchestrate optimal agent collaboration"
    }
}


@router.get("/agents")
async def list_agents():
    """List all available agents"""
    return {
        "agents": list(AGENTS.values()),
        "count": len(AGENTS)
    }


@router.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get detailed information about a specific agent"""
    # Normalize the ID
    normalized_id = agent_id.lower().replace("_", "-")
    
    if normalized_id in AGENTS:
        return AGENTS[normalized_id]
    
    return JSONResponse(
        status_code=404,
        content={"error": f"Agent {agent_id} not found"}
    )
