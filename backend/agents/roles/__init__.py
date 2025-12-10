"""
MetaGPT Role-based Agents for FlagPilot
"""

from .contract_guardian import ContractGuardian
from .job_authenticator import JobAuthenticator
from .payment_enforcer import PaymentEnforcer
from .talent_vet import TalentVet
from .ghosting_shield import GhostingShield
from .scope_sentinel import ScopeSentinel
from .dispute_mediator import DisputeMediator
from .profile_analyzer import ProfileAnalyzer
from .communication_coach import CommunicationCoach
from .negotiation_assistant import NegotiationAssistant
from .application_filter import ApplicationFilter
from .feedback_loop import FeedbackLoop
from .flagpilot_orchestrator import FlagPilotOrchestrator
from .risk_advisor import RiskAdvisor

__all__ = [
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
    "RiskAdvisor",
]
