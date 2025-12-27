"""
Intelligent Agent Router - LLM-Based Selection
==============================================
Replaces naive keyword matching with semantic understanding.
Uses LLM to analyze task and select appropriate agents with confidence.
"""

from typing import List, Dict, Any, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger
import json


# Agent registry with detailed descriptions for LLM routing
AGENT_REGISTRY = {
    "risk-advisor": {
        "description": "Scam detection and critical risk assessment. Use for suspicious job offers, check fraud, Telegram/WhatsApp schemes.",
        "triggers": ["scam", "fraud", "suspicious", "too good to be true", "check", "telegram"]
    },
    "contract-guardian": {
        "description": "Contract analysis, legal terms review, IP rights, payment structures, termination clauses.",
        "triggers": ["contract", "agreement", "clause", "legal", "terms", "NDA", "IP"]
    },
    "job-authenticator": {
        "description": "Job posting verification, company legitimacy checks, red flag detection in offers.",
        "triggers": ["job", "offer", "posting", "hiring", "opportunity", "company"]
    },
    "payment-enforcer": {
        "description": "Invoice collection, overdue payments, payment disputes, financial protection.",
        "triggers": ["payment", "invoice", "overdue", "owed", "pay", "money", "collect"]
    },
    "scope-sentinel": {
        "description": "Scope creep detection, change request analysis, project boundary protection.",
        "triggers": ["scope", "creep", "extra", "additional", "change", "revision", "more work"]
    },
    "negotiation-assistant": {
        "description": "Rate negotiation, pricing strategy, compensation benchmarks, deal structure.",
        "triggers": ["rate", "negotiate", "price", "charge", "budget", "worth", "salary"]
    },
    "communication-coach": {
        "description": "Professional email drafting, client messages, proposal writing, response templates.",
        "triggers": ["email", "draft", "write", "message", "reply", "communicate", "proposal"]
    },
    "dispute-mediator": {
        "description": "Conflict resolution, evidence analysis, mediation strategies, client disputes.",
        "triggers": ["dispute", "conflict", "disagree", "problem", "complaint", "issue"]
    },
    "ghosting-shield": {
        "description": "Client re-engagement, follow-up strategies, non-responsive client handling.",
        "triggers": ["ghost", "silent", "no response", "follow up", "disappeared"]
    },
    "profile-analyzer": {
        "description": "Client research, company profiling, background checks, reputation analysis.",
        "triggers": ["client", "company", "background", "profile", "research", "review"]
    },
}

ROUTER_SYSTEM_PROMPT = """You are an intelligent task router for FlagPilot, a freelancer protection platform.

Analyze the user's request and select the most appropriate specialist agents.

Available agents:
{agents_list}

RULES:
1. Select 1-4 agents maximum
2. Prioritize agents that directly address the user's needs
3. If task involves multiple concerns, select multiple agents
4. For scam/fraud indicators, ALWAYS include "risk-advisor" first
5. Return ONLY a JSON object with:
   - "agents": list of agent IDs
   - "reasoning": brief explanation
   - "urgency": "low", "medium", "high", or "critical"

Example output:
{{"agents": ["contract-guardian", "negotiation-assistant"], "reasoning": "Contract review with rate negotiation needed", "urgency": "medium"}}"""


async def llm_route_agents(task: str, context: Dict[str, Any] = None) -> Tuple[List[str], str, str]:
    """
    Use LLM to intelligently route task to appropriate agents.
    Returns: (agent_ids, reasoning, urgency)
    """
    from config import get_llm
    
    # Build agents list for prompt
    agents_list = "\n".join([
        f"- {aid}: {info['description']}" 
        for aid, info in AGENT_REGISTRY.items()
    ])
    
    llm = get_llm(temperature=0.1)  # Low temp for consistent routing
    
    try:
        response = await llm.ainvoke([
            SystemMessage(content=ROUTER_SYSTEM_PROMPT.format(agents_list=agents_list)),
            HumanMessage(content=f"Route this task to the appropriate agents:\n\n{task}")
        ])
        
        # Parse JSON response
        content = response.content.strip()
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        result = json.loads(content)
        agents = result.get("agents", [])[:4]  # Max 4 agents
        reasoning = result.get("reasoning", "")
        urgency = result.get("urgency", "medium")
        
        logger.info(f"🧠 LLM Router: {agents} (urgency: {urgency})")
        logger.debug(f"Reasoning: {reasoning}")
        
        # Validate agent IDs
        valid_agents = [a for a in agents if a in AGENT_REGISTRY]
        
        if not valid_agents:
            # Fallback to default agents
            valid_agents = ["profile-analyzer", "communication-coach"]
        
        return valid_agents, reasoning, urgency
        
    except Exception as e:
        logger.warning(f"LLM routing failed, falling back to keyword: {e}")
        # Fallback to keyword-based routing
        return fallback_keyword_route(task), "Keyword fallback", "medium"


def fallback_keyword_route(task: str) -> List[str]:
    """Fallback keyword-based routing when LLM fails."""
    task_lower = task.lower()
    relevant = []
    
    for agent_id, info in AGENT_REGISTRY.items():
        if any(trigger in task_lower for trigger in info["triggers"]):
            relevant.append(agent_id)
    
    if not relevant:
        relevant = ["profile-analyzer", "communication-coach"]
    
    return relevant[:4]


# Export for orchestrator use
__all__ = ["llm_route_agents", "fallback_keyword_route", "AGENT_REGISTRY"]
