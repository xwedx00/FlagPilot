"""
FlagPilot Agents - MetaGPT-based Multi-Agent System
====================================================
13 specialized agents using MetaGPT Role class with Team orchestration.

Agents can work:
1. Independently - Direct API calls to single agents
2. As a Team - Orchestrated by FlagPilot agent using MetaGPT Environment
"""

from .roles import (
    ContractGuardian,
    JobAuthenticator,
    PaymentEnforcer,
    TalentVet,
    GhostingShield,
    ScopeSentinel,
    DisputeMediator,
    ProfileAnalyzer,
    CommunicationCoach,
    NegotiationAssistant,
    ApplicationFilter,
    FeedbackLoop,
    FlagPilotOrchestrator,
)

from .team import FlagPilotTeam, run_team_task

__all__ = [
    # Individual Roles
    "ContractGuardian",
    "JobAuthenticator", 
    "PaymentEnforcer",
    "TalentVet",
    "GhostingShield",
    "ScopeSentinel",
    "DisputeMediator",
    "ProfileAnalyzer",
    "CommunicationCoach",
    "NegotiationAssistant",
    "ApplicationFilter",
    "FeedbackLoop",
    "FlagPilotOrchestrator",
    # Team
    "FlagPilotTeam",
    "run_team_task",
]

# Agent registry for API
AGENT_REGISTRY = {
    "contract-guardian": ContractGuardian,
    "job-authenticator": JobAuthenticator,
    "payment-enforcer": PaymentEnforcer,
    "talent-vet": TalentVet,
    "ghosting-shield": GhostingShield,
    "scope-sentinel": ScopeSentinel,
    "dispute-mediator": DisputeMediator,
    "profile-analyzer": ProfileAnalyzer,
    "communication-coach": CommunicationCoach,
    "negotiation-assistant": NegotiationAssistant,
    "application-filter": ApplicationFilter,
    "feedback-loop": FeedbackLoop,
    "flagpilot": FlagPilotOrchestrator,
}



# Centralized mapping from backend agent IDs to frontend agent IDs
# Frontend has different naming for some agents
AGENT_ID_MAP = {
    "contract-guardian": "legal-eagle",
    "job-authenticator": "job-authenticator",
    "payment-enforcer": "payment-enforcer",
    "talent-vet": "coach",
    "ghosting-shield": "connector",
    "scope-sentinel": "scope-sentinel",
    "dispute-mediator": "adjudicator",
    "profile-analyzer": "coach",
    "communication-coach": "connector",
    "negotiation-assistant": "negotiator",
    "application-filter": "job-authenticator",
    "feedback-loop": "scribe",
    "flagpilot": "flagpilot",
}

def get_frontend_agent_id(backend_id: str) -> str:
    """Convert backend agent ID to frontend agent ID"""
    return AGENT_ID_MAP.get(backend_id, backend_id)

