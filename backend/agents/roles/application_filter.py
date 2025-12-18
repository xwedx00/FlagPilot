"""
Application Filter - Job Application Screening Agent
"""

from typing import ClassVar
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class FilterApplication(FlagPilotAction):
    """Screen job applications for fit and quality"""
    
    name: str = "FilterApplication"
    desc: str = "Evaluate applications against job criteria to save client time."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Application Filter, screening freelancer proposals.
    
    Job Description / Criteria (RAG):
    {rag_context}
    
    Proposal / Application:
    {content}
    
    Evaluate:
    1. RELEVANCE SCORE (1-10)
    2. KEY QUALIFICATIONS MET (Yes/No list)
    3. PROPOSAL QUALITY (Personalized vs Generic)
    4. RED FLAGS (Spam, bot-like, irrelevant)
    
    Recommendation: SHORTLIST, MAYBE, or REJECT.
    """

    async def run(self, instruction: str, context: str = "") -> str:
        # 1. Native Tool: Search for job details if looking at a specific application
        rag_context = "Standard screening criteria."
        try:
            rag_context = await RAGSearch.search_knowledge_base(
                query=f"job description qualifications {instruction[:50]}", 
                top_k=2
            )
        except Exception:
            pass

        # 2. Build Prompt
        prompt = self.PROMPT_TEMPLATE.format(
            content=instruction,
            # Context might contain the job ID or specific requirements passed by the orchestrator
            rag_context=f"{rag_context}\n\nJob Context: {context}"
        )
        
        # 3. Call LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)


class ApplicationFilter(FlagPilotRole):
    """
    Application Filter Agent
    Watches for: New proposals on posted jobs
    """
    
    name: str = "ApplicationFilter"
    profile: str = "Recruitment Screening Specialist"
    goal: str = "Save client time by filtering irrelevant or low-quality proposals"
    constraints: str = "Be fair, look for hidden gems, filter out spam"
    
    def __init__(self, **kwargs):
        super().__init__(actions=[FilterApplication], **kwargs)
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = FilterApplication()
        return await action.run(instruction=text, context=str(context))
