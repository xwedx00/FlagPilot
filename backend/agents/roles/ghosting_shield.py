"""
Ghosting Shield - Follow-up Strategy Agent
"""

from typing import ClassVar
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class ShieldGhosting(FlagPilotAction):
    """Create follow-up strategies for unresponsive clients"""
    
    name: str = "ShieldGhosting"
    desc: str = "Plan follow-up sequences for ghosting clients."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Ghosting Shield, re-engaging clients who went silent.
    
    Follow-up Strategy / Sequences (RAG):
    {rag_context}
    
    Situation:
    {content}
    
    Provide:
    1. DIAGNOSIS (Why might they be silent? Busy? Not interested?)
    2. STRATEGY (Wait? Call? Email?)
    3. THE "MAGIC EMAIL" (A specific script designed to get a response)
    4. THE "BREAK UP" EMAIL (Last resort script)
    
    Be persistent but never desperate.
    """

    async def run(self, instruction: str, context: str = "") -> str:
        # 1. Native Tool: Search for follow-up timing and templates
        rag_context = "General follow-up advice."
        try:
            rag_context = await RAGSearch.search_knowledge_base(
                query=f"client ghosting follow up email {instruction[:50]}", 
                top_k=2
            )
        except Exception:
            pass

        # 2. Build Prompt
        prompt = self.PROMPT_TEMPLATE.format(
            content=instruction,
            rag_context=f"{rag_context}\n\nProject History: {context}"
        )
        
        # 3. Call LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)


class GhostingShield(FlagPilotRole):
    """
    Ghosting Shield Agent
    Watches for: Unanswered messages, stalled projects
    """
    
    name: str = "GhostingShield"
    profile: str = "Client Re-engagement Specialist"
    goal: str = "Help freelancers re-engage unresponsive clients professionally"
    constraints: str = "Be persistent but professional, know when to move on"
    
    def __init__(self, **kwargs):
        super().__init__(actions=[ShieldGhosting], **kwargs)
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = ShieldGhosting()
        return await action.run(instruction=text, context=str(context))
