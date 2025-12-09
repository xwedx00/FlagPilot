"""
Feedback Loop - Continuous Improvement Agent
"""

from typing import ClassVar
from agents.roles.base_role import FlagPilotRole, FlagPilotAction
from config import get_configured_llm
from lib.tools.rag_tool import RAGSearch

class AnalyzeFeedback(FlagPilotAction):
    """Analyze feedback to improve future performance"""
    
    name: str = "AnalyzeFeedback"
    desc: str = "Connect project outcomes to future improvements."
    
    PROMPT_TEMPLATE: ClassVar[str] = """
    You are Feedback Loop, turning experience into growth.
    
    Historical Feedback / Lessons Learned (RAG):
    {rag_context}
    
    Current Feedback / Situation:
    {content}
    
    Analyze:
    1. SENTIMENT ANALYSIS (Positive/Neutral/Negative)
    2. KEY THEMES (Communication, Quality, Speed)
    3. ACTIONABLE IMPROVEMENTS for next time
    4. RESPONSE DRAFT (to the person giving feedback)
    
    Focus on constructive growth.
    """

    async def run(self, instruction: str, context: str = "") -> str:
        # 1. Native Tool: Search for past feedback patterns
        rag_context = "First feedback entry."
        try:
            rag_context = RAGSearch.search_knowledge_base(
                query=f"client feedback history lessons {instruction[:50]}", 
                top_k=3
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


class FeedbackLoop(FlagPilotRole):
    """
    Feedback Loop Agent
    Watches for: Project completion, rating submission
    """
    
    name: str = "FeedbackLoop"
    profile: str = "Continuous Improvement Specialist"
    goal: str = "Help freelancers improve by analyzing feedback patterns"
    constraints: str = "Be constructive, identify patterns, suggest actionable changes"
    
    def __init__(self, **kwargs):
        super().__init__(actions=[AnalyzeFeedback], **kwargs)
        
    async def analyze(self, text: str, context: dict = None) -> str:
        """Override for direct API usage"""
        action = AnalyzeFeedback()
        return await action.run(instruction=text, context=str(context))
