"""
Negotiation Assistant - Rate & Term Negotiation Agent
"""

from typing import ClassVar
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class AssistNegotiation(FlagPilotAction):
    """Help with rate and salary negotiations"""
    
    name: str = "AssistNegotiation"
    desc: str = "Analyze negotiation scenarios and provide strategies/scripts."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Negotiation Assistant, an expert negotiator for freelancers.
    
    Market Data / RAG Context:
    {rag_context}
    
    Analyze this negotiation scenario:
    {content}
    
    Provide:
    1. LEVERAGE ANALYSIS (What power do you have?)
    2. RATE GUIDANCE (Based on market context if available)
    3. SPECIFIC SCRIPTS for the next email/call
    4. RESPONSES to likely pushbacks
    
    Focus on value-based pricing and win-win outcomes.
    """

    async def run(self, instruction: str, context: str = "") -> str:
        # 1. Native Tool: Search for market rates or similar negotiation history
        rag_context = "No specific market data found."
        try:
            rag_context = await RAGSearch.search_knowledge_base(
                query=f"market rate negotiation strategy {instruction[:50]}", 
                top_k=2
            )
        except Exception:
            pass

        # 2. Build Prompt
        prompt = self.PROMPT_TEMPLATE.format(
            content=instruction,
            # If explicit context is provided (e.g. from file upload), append it to RAG context
            rag_context=f"{rag_context}\n\nUser Context: {context}"
        )
        
        # 3. Call LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)


class NegotiationAssistant(FlagPilotRole):
    """
    Negotiation Assistant Agent
    Watches for: Rate discussions, contract offers
    """
    
    name: str = "NegotiationAssistant"
    profile: str = "Negotiation Strategy Specialist"
    goal: str = "Help freelancers negotiate fair rates and terms"
    constraints: str = "Be realistic, know market rates, maintain professionalism"
    
    def __init__(self, **kwargs):
        super().__init__(actions=[AssistNegotiation], **kwargs)
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = AssistNegotiation()
        return await action.run(instruction=text, context=str(context))
