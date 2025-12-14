"""
Communication Coach - Message Improvement Agent
"""

from typing import ClassVar
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class CoachCommunication(FlagPilotAction):
    """Improve client communication"""
    
    name: str = "CoachCommunication"
    desc: str = "Refine drafts and suggest better communication styles."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Communication Coach, ensuring professional and effective messages.
    
    Style Guide / Best Practices (RAG):
    {rag_context}
    
    Draft Message:
    {content}
    
    Analyze & Improve:
    1. TONE CHECK (Is it professional? Passive-aggressive? Too casual?)
    2. CLARITY CHECK (Is the call to action clear?)
    3. POLISHED VERSION (Better phrasing)
    4. ALTERNATIVE STRATEGY (If the message intent itself is flawed)
    
    Aim for clarity, confidence, and professionalism.
    """

    async def run(self, instruction: str, context: str = "") -> str:
        # 1. Native Tool: Search for communication templates
        rag_context = "General professional standards."
        try:
            rag_context = await RAGSearch.search_knowledge_base(
                query=f"email template client communication {instruction[:50]}", 
                top_k=2
            )
        except Exception:
            pass

        # 2. Build Prompt
        prompt = self.PROMPT_TEMPLATE.format(
            content=instruction,
            rag_context=f"{rag_context}\n\nContext: {context}"
        )
        
        # 3. Call LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)


class CommunicationCoach(FlagPilotRole):
    """
    Communication Coach Agent
    Watches for: Draft messages, email replies
    """
    
    name: str = "CommunicationCoach"
    profile: str = "Professional Communication Specialist"
    goal: str = "Help freelancers communicate clearly and professionally"
    constraints: str = "Improve without changing meaning, consider cultural context"
    
    def __init__(self, **kwargs):
        super().__init__(actions=[CoachCommunication], **kwargs)
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = CoachCommunication()
        return await action.run(instruction=text, context=str(context))
