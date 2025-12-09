"""
Dispute Mediator - Conflict Resolution Agent
"""

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from typing import ClassVar
from config import get_configured_llm


class MediateDispute(Action):
    """Resolve conflicts between freelancers and clients"""
    
    name: str = "MediateDispute"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Dispute Mediator, an expert at resolving conflicts between freelancers and clients.

Analyze this dispute and provide:
1. BOTH PERSPECTIVES understanding
2. CORE ISSUES identification
3. COMMON GROUND finding
4. WIN-WIN SOLUTIONS
5. COMMUNICATION TEMPLATES
6. DOCUMENTATION recommendations

Dispute/conflict:
{content}

Context:
{context}

Provide mediation strategies that resolve disputes while preserving professional relationships.
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class DisputeMediator(Role):
    """Dispute Mediator Agent - Conflict resolution"""
    
    name: str = "DisputeMediator"
    profile: str = "Conflict Resolution Specialist"
    goal: str = "Resolve disputes fairly while preserving professional relationships"
    constraints: str = "Be neutral, focus on solutions, document agreements"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([MediateDispute])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await MediateDispute().run(content=text, context=ctx)
