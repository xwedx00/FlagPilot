"""
CopilotKit SDK Setup - LangGraph AG-UI Integration
====================================================
Configures the AG-UI endpoint with FlagPilot LangGraph agent.

Uses the new AG-UI protocol for streaming agent state to the frontend.
Documentation: https://docs.copilotkit.ai/langgraph
"""

from copilotkit import LangGraphAGUIAgent
from .graph import graph

# Create the LangGraph AG-UI Agent
flagpilot_agent = LangGraphAGUIAgent(
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

# Log initialization
print(f"[CopilotKit SDK] Initialized agent: {flagpilot_agent.name}")
