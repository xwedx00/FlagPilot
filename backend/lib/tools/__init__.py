"""
FlagPilot Agent Tools
======================
Production-grade LangChain tools for all 14 agents.

21 Advanced Tools:
- RAG Tools (3): Knowledge search, user context, save learning
- Scam Tools (4): Company verify, email analysis, scam check, report generation
- Contract Tools (4): Clause analysis, jurisdiction check, redlines, liability calc
- Financial Tools (4): Overdue calc, invoice gen, collection letters, scope creep
- Market Tools (3): Rate lookup, proposal benchmark, budget analysis
- Communication Tools (3): Email drafting, sentiment analysis, translation
"""

from .base import ToolMetrics, ToolResult, ToolError, track_tool

from .rag_tools import (
    RAG_TOOLS,
    search_knowledge_base,
    get_user_context,
    save_learning,
)

from .scam_tools import (
    SCAM_TOOLS,
    verify_company_existence,
    analyze_email_headers,
    check_scam_database,
    generate_scam_report,
)

from .contract_tools import (
    CONTRACT_TOOLS,
    analyze_contract_clauses,
    check_jurisdiction_laws,
    generate_contract_redlines,
    calculate_liability_exposure,
)

from .financial_tools import (
    FINANCIAL_TOOLS,
    calculate_overdue_amount,
    generate_invoice,
    draft_collection_letter,
    estimate_project_value,
)

from .market_tools import (
    MARKET_TOOLS,
    get_market_rates,
    benchmark_proposal,
    analyze_client_budget,
)

from .communication_tools import (
    COMMUNICATION_TOOLS,
    draft_professional_email,
    analyze_sentiment,
    translate_message,
)


# =============================================================================
# Tool Collections by Agent
# =============================================================================

def get_tools_for_agent(agent_name: str) -> list:
    """Get the appropriate tools for a specific agent."""
    
    # All agents get RAG tools
    base_tools = list(RAG_TOOLS)
    
    # Agent-specific tools
    agent_tools = {
        "contract-guardian": CONTRACT_TOOLS,
        "job-authenticator": SCAM_TOOLS,
        "risk-advisor": SCAM_TOOLS,
        "scope-sentinel": FINANCIAL_TOOLS,
        "payment-enforcer": FINANCIAL_TOOLS,
        "negotiation-assistant": MARKET_TOOLS,
        "communication-coach": COMMUNICATION_TOOLS,
        "profile-analyzer": SCAM_TOOLS[:2],  # Company verify, email analysis
        "dispute-mediator": CONTRACT_TOOLS[:2] + COMMUNICATION_TOOLS,
        "talent-vet": MARKET_TOOLS + [analyze_sentiment],
        "ghosting-shield": COMMUNICATION_TOOLS + [draft_collection_letter],
        "application-filter": [analyze_sentiment, get_market_rates],
        "feedback-loop": [save_learning, analyze_sentiment],
        "planner-role": [estimate_project_value, get_market_rates],
    }
    
    specific = agent_tools.get(agent_name, [])
    
    # Combine and deduplicate
    all_tools = base_tools + list(specific)
    seen = set()
    unique_tools = []
    for tool in all_tools:
        if tool.name not in seen:
            seen.add(tool.name)
            unique_tools.append(tool)
    
    return unique_tools


# All tools combined
ALL_TOOLS = (
    list(RAG_TOOLS) + 
    list(SCAM_TOOLS) + 
    list(CONTRACT_TOOLS) + 
    list(FINANCIAL_TOOLS) + 
    list(MARKET_TOOLS) + 
    list(COMMUNICATION_TOOLS)
)


__all__ = [
    # Base
    "ToolMetrics",
    "ToolResult",
    "ToolError",
    "track_tool",
    
    # Collections
    "RAG_TOOLS",
    "SCAM_TOOLS",
    "CONTRACT_TOOLS",
    "FINANCIAL_TOOLS",
    "MARKET_TOOLS",
    "COMMUNICATION_TOOLS",
    "ALL_TOOLS",
    
    # Helper
    "get_tools_for_agent",
    
    # Individual Tools
    "search_knowledge_base",
    "get_user_context",
    "save_learning",
    "verify_company_existence",
    "analyze_email_headers",
    "check_scam_database",
    "generate_scam_report",
    "analyze_contract_clauses",
    "check_jurisdiction_laws",
    "generate_contract_redlines",
    "calculate_liability_exposure",
    "calculate_overdue_amount",
    "generate_invoice",
    "draft_collection_letter",
    "estimate_project_value",
    "get_market_rates",
    "benchmark_proposal",
    "analyze_client_budget",
    "draft_professional_email",
    "analyze_sentiment",
    "translate_message",
]
