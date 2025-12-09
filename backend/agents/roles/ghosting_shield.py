"""
Ghosting Shield - Follow-up Strategy Agent
"""

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from typing import ClassVar
from config import get_configured_llm


class ShieldGhosting(Action):
    """Create follow-up strategies for unresponsive clients"""
    
    name: str = "ShieldGhosting"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Ghosting Shield, an expert at re-engaging unresponsive clients professionally.

Create a follow-up strategy for:
1. SITUATION ASSESSMENT (project stage, last contact, relationship)
2. TIMING RECOMMENDATIONS for follow-ups
3. MESSAGE TEMPLATES (ready to send)
4. ALTERNATIVE CHANNELS to try
5. WHEN TO MOVE ON

Situation:
{content}

Context:
{context}

Provide professional templates that are persistent but not pushy.
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class GhostingShield(Role):
    """Ghosting Shield Agent - Follow-up strategies"""
    
    name: str = "GhostingShield"
    profile: str = "Client Re-engagement Specialist"
    goal: str = "Help freelancers re-engage unresponsive clients professionally"
    constraints: str = "Be persistent but professional, know when to move on"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([ShieldGhosting])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await ShieldGhosting().run(content=text, context=ctx)
