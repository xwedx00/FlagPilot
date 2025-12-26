"""
CopilotKit SDK Setup
====================
Configures the CopilotKitRemoteEndpoint with FlagPilot agents.

Uses LangGraphAgent (the standard agent type for LangGraph integrations).
The agent wraps the MetaGPT orchestration through a LangGraph workflow.
"""

from copilotkit import CopilotKitRemoteEndpoint
from copilotkit import LangGraphAgent
from .graph import graph

# Patch LangGraphAgent to add missing dict_repr
class FixedLangGraphAgent(LangGraphAgent):
    def dict_repr(self):
        return {
            'name': self.name,
            'description': self.description or ''
        }

# Create the CopilotKit SDK with our LangGraph agent
sdk = CopilotKitRemoteEndpoint(
    agents=[
        FixedLangGraphAgent(
            name="flagpilot_orchestrator",
            description="""FlagPilot multi-agent team for freelancer protection.

Capabilities:
- Contract analysis for legal risks and unfair clauses
- Job posting authentication and scam detection
- Payment enforcement and invoice tracking
- Scope creep detection and prevention
- Client communication coaching
- Dispute mediation
- Profile optimization
- Rate negotiation assistance

The team coordinates 17 specialized AI agents to provide comprehensive protection for freelancers.""",
            graph=graph,
        )
    ]
)

# Debug: Print loaded agents
print(f"[CopilotKit SDK] Initialized with agents: {[a.name for a in sdk.agents]}")
