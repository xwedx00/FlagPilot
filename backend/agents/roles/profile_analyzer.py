"""
Profile Analyzer - Profile Optimization Agent
"""

from typing import ClassVar
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class AnalyzeProfile(FlagPilotAction):
    """Optimize freelancer profiles"""
    
    name: str = "AnalyzeProfile"
    desc: str = "Analyze profile metrics and suggest SEO/content improvements."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Profile Analyzer, maximizing freelancer visibility.
    
    Industry Keywords / Trends (RAG):
    {rag_context}
    
    Profile to Analyze:
    {content}
    
    Provide:
    1. VISIBILITY SCORE (1-10)
    2. SEO KEYWORD GAP ANALYSIS (What's missing?)
    3. HEADLINE MAKEOVER (3 variations)
    4. SUMMARY REWRITE suggesting (Focus on benefits, not just features)
    5. PORTFOLIO PRESENTATION tips
    
    Focus on conversion: turning views into interviews.
    """

    async def run(self, instruction: str, context: str = "") -> str:
        # 1. Native Tool: Search for industry keywords (e.g., "React Developer keywords")
        rag_context = "General best practices."
        try:
            rag_context = RAGSearch.search_knowledge_base(
                query=f"high paying keywords skills {instruction[:50]}", 
                top_k=3
            )
        except Exception:
            pass

        # 2. Build Prompt
        prompt = self.PROMPT_TEMPLATE.format(
            content=instruction,
            rag_context=f"{rag_context}\n\nClient Target: {context}"
        )
        
        # 3. Call LLM
        llm = get_configured_llm()
        return await llm.aask(prompt)


class ProfileAnalyzer(FlagPilotRole):
    """
    Profile Analyzer Agent
    Watches for: User profile updates, optimization requests
    """
    
    name: str = "ProfileAnalyzer"
    profile: str = "Profile Optimization Specialist"
    goal: str = "Help freelancers create compelling profiles that attract ideal clients"
    constraints: str = "Be specific, suggest keywords, consider platform SEO"
    
    def __init__(self, **kwargs):
        super().__init__(actions=[AnalyzeProfile], **kwargs)
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = AnalyzeProfile()
        return await action.run(instruction=text, context=str(context))
