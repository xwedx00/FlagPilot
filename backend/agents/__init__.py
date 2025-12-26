"""
FlagPilot Agents Package
========================
LangGraph-based multi-agent system for freelancer protection.
"""

from agents.agents import (
    FlagPilotAgent,
    get_agent,
    get_all_agents,
    list_agents,
    AGENTS,
    # Individual agents
    ContractGuardian,
    JobAuthenticator,
    RiskAdvisor,
    ScopeSentinel,
    PaymentEnforcer,
    NegotiationAssistant,
    CommunicationCoach,
    DisputeMediator,
    GhostingShield,
    ProfileAnalyzer,
    TalentVet,
    ApplicationFilter,
    FeedbackLoop,
    PlannerRole,
)
from agents.orchestrator import orchestrator_graph, run_orchestrator, OrchestratorState

__all__ = [
    "FlagPilotAgent",
    "get_agent",
    "get_all_agents", 
    "list_agents",
    "AGENTS",
    "orchestrator_graph",
    "run_orchestrator",
    "OrchestratorState",
]
