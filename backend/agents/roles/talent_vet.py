"""
Talent Vet - Profile Evaluation Agent
"""

from typing import ClassVar
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class VetTalent(FlagPilotAction):
    """Evaluate freelancer profiles and portfolios"""
    
    name: str = "VetTalent"
    desc: str = "Evaluate profiles against industry standards and job requirements."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Talent Vet, an expert at scouting top-tier freelancers.
    
    Job Description / Criteria (RAG):
    {rag_context}
    
    Candidate Profile / Portfolio:
    {content}
    
    Evaluate:
    1. MATCH SCORE (1-10) against criteria
    2. KEY STRENGTHS aligned with project
    3. RED FLAGS / INCONSISTENCIES
    4. RECOMMENDED INTERVIEW QUESTIONS to verify skills
    
    Be objective and critical. High standards protect the client.
    """

    async def run(self, instruction: str, context: str = "") -> str:
        # 1. Native Tool: Search for specific job requirements if not fully provided
        rag_context = "Standard evaluation criteria."
        try:
            # Search for specific role requirements mentioned in the profile (e.g., "Senior Python Dev requirements")
            rag_context = RAGSearch.search_knowledge_base(
                query=f"job requirements criteria {instruction[:50]}", 
                top_k=2
            )
        except Exception:
            pass

        # 2. Build Prompt
        prompt = self.PROMPT_TEMPLATE.format(
            content=instruction,
            rag_context=f"{rag_context}\n\nProject Context: {context}"
        )
        
        # 3. Call LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)


class TalentVet(FlagPilotRole):
    """
    Talent Vet Agent
    Watches for: Resume uploads, candidate profiles
    """
    
    name: str = "TalentVet"
    profile: str = "Talent Evaluation Specialist"
    goal: str = "Help clients find quality freelancers by evaluating profiles"
    constraints: str = "Be objective, verify claims, suggest verification methods"
    
    def __init__(self, **kwargs):
        super().__init__(actions=[VetTalent], **kwargs)
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = VetTalent()
        return await action.run(instruction=text, context=str(context))
