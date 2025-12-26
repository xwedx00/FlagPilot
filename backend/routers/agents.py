"""
FlagPilot Agents Router
=======================
Provides agent metadata endpoints.
Agents are implemented using LangGraph and orchestrated via the multi-agent supervisor.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from loguru import logger

router = APIRouter(prefix="/api", tags=["Agents"])

# Agent metadata - matches the LangGraph agent registry
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
        "description": "Analyzes client profiles and reputation",
        "profile": "Profile Analysis Expert",
        "goal": "Help vet potential clients"
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
        "description": "Provides critical safety protocols for high-risk situations",
        "profile": "Risk Management Consultant",
        "goal": "Protect freelancers from fraud and scams"
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
    }
}


@router.get("/agents")
async def list_agents():
    """List all available agents"""
    return {
        "agents": list(AGENTS.values()),
        "count": len(AGENTS),
        "framework": "LangGraph"
    }


@router.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get detailed information about a specific agent"""
    normalized_id = agent_id.lower().replace("_", "-")
    
    if normalized_id in AGENTS:
        return AGENTS[normalized_id]
    
    return JSONResponse(
        status_code=404,
        content={"error": f"Agent {agent_id} not found"}
    )
