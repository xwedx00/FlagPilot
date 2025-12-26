"""
CopilotKit SDK Setup - LangGraph Integration
=============================================
Configures the CopilotKitRemoteEndpoint with FlagPilot agents.

Uses LangGraphAgent for native LangGraph workflow integration.
"""

from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from .graph import graph

# Create the CopilotKit SDK with FlagPilot LangGraph agent
sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="flagpilot_orchestrator",
            description="""FlagPilot - AI-powered freelancer protection team.

🛡️ **Capabilities:**
• **Contract Analysis** - Review contracts for legal risks and unfair clauses
• **Scam Detection** - Verify job postings and detect fraudulent offers (Fast-Fail enabled)
• **Payment Protection** - Track invoices and create collection strategies
• **Scope Creep Detection** - Identify boundary violations and extra work requests
• **Client Communication** - Draft professional messages and proposals
• **Rate Negotiation** - Get market data and negotiation strategies
• **Dispute Resolution** - Navigate conflicts and platform disputes
• **Profile Optimization** - Vet clients and improve your freelance profile

🤖 **Powered by 14 specialized LangGraph AI agents** working together to protect your freelance business.

⚡ **Smart Features:**
• Real-time risk assessment
• RAG-enhanced knowledge base
• Persistent memory across sessions
• Fast-fail on critical risks (scams, fraud)""",
            graph=graph,
        )
    ]
)

# Log initialization
print(f"[CopilotKit SDK] Initialized with agents: {[a.name for a in sdk.agents]}")
