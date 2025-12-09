"""
Feedback Loop - Feedback Processing Agent
"""

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from typing import ClassVar
from config import get_configured_llm


class ProcessFeedback(Action):
    """Process and learn from user feedback"""
    
    name: str = "ProcessFeedback"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Feedback Loop, an expert at analyzing user feedback and extracting actionable insights.

Analyze this feedback for:
1. CATEGORY (bug, feature, usability, praise, suggestion)
2. SENTIMENT analysis
3. KEY ISSUES extracted
4. PATTERNS identified
5. IMPROVEMENT suggestions
6. PRIORITY rating

Feedback to analyze:
{content}

Context:
{context}

Provide actionable insights to improve the platform.
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class FeedbackLoop(Role):
    """Feedback Loop Agent - Feedback processing"""
    
    name: str = "FeedbackLoop"
    profile: str = "Feedback Analysis Specialist"
    goal: str = "Turn user feedback into platform improvements"
    constraints: str = "Be objective, prioritize by impact, track patterns"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([ProcessFeedback])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await ProcessFeedback().run(content=text, context=ctx)
