"""
CopilotKit SDK Setup
====================
Configures the CopilotKitRemoteEndpoint with FlagPilot agents.
"""

from copilotkit import CopilotKitRemoteEndpoint
from copilotkit.langgraph_agui_agent import LangGraphAGUIAgent
from .graph import graph

# Create the CopilotKit SDK with our LangGraph agent
sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAGUIAgent(
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
