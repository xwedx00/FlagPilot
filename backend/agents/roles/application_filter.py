"""
Application Filter - Spam/AI Detection Agent
"""

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from typing import ClassVar
from config import get_configured_llm


class FilterApplication(Action):
    """Filter spam and AI-generated applications"""
    
    name: str = "FilterApplication"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Application Filter, an expert at identifying genuine vs spam/AI-generated job applications.

Analyze this application for:
1. AI/GENERATED content indicators
2. TEMPLATE usage detection
3. JOB RELEVANCE assessment
4. EXPERIENCE VERIFICATION flags
5. AUTHENTICITY scoring
6. RECOMMENDATION

Application to analyze:
{content}

Job requirements:
{context}

Provide analysis to help find genuine, qualified candidates.
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class ApplicationFilter(Role):
    """Application Filter Agent - Spam/AI detection"""
    
    name: str = "ApplicationFilter"
    profile: str = "Application Screening Specialist"
    goal: str = "Help clients identify genuine applicants from spam and AI-generated content"
    constraints: str = "Be fair, look for substance, consider context"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([FilterApplication])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await FilterApplication().run(content=text, context=ctx)
