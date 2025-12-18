"""
Dispute Mediator - Conflict Resolution Agent
"""

from typing import ClassVar
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class MediateDispute(FlagPilotAction):
    """Resolve conflicts between freelancers and clients"""
    
    name: str = "MediateDispute"
    desc: str = "Analyze disputes and provide fair resolution strategies."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Dispute Mediator, a neutral conflict resolution expert.
    
    Relevant Precedents / Contract Terms (RAG):
    {rag_context}
    
    Analyze this dispute:
    {content}
    
    Provide:
    1. OBJECTIVE SUMMARY of the conflict
    2. PROPOSED RESOLUTION (Fair to both parties)
    3. COMMUNICATION TEMPLATES to de-escalate
    4. PREVENTATIVE MEASURES for future
    
    Prioritize de-escalation and professional relationships.
    """

    async def run(self, instruction: str, context: str = "") -> str:
        # 1. Native Tool: Search for similar disputes or standard contract clauses regarding disputes
        rag_context = "No specific precedents found."
        try:
            rag_context = await RAGSearch.search_knowledge_base(
                query=f"dispute resolution contract clause {instruction[:50]}", 
                top_k=2
            )
        except Exception:
            pass

        # 2. Build Prompt
        prompt = self.PROMPT_TEMPLATE.format(
            content=instruction,
            rag_context=f"{rag_context}\n\nCase Details: {context}"
        )
        
        # 3. Call LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)


class DisputeMediator(FlagPilotRole):
    """
    Dispute Mediator Agent
    Watches for: Conflict language, negative feedback
    """
    
    name: str = "DisputeMediator"
    profile: str = "Conflict Resolution Specialist"
    goal: str = "Resolve disputes fairly while preserving professional relationships"
    constraints: str = "Be neutral, focus on solutions, document agreements"
    
    def __init__(self, **kwargs):
        super().__init__(actions=[MediateDispute], **kwargs)
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = MediateDispute()
        return await action.run(instruction=text, context=str(context))
