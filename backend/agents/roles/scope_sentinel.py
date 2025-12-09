"""
Scope Sentinel - Scope Creep Detection Agent
"""

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from typing import ClassVar
from config import get_configured_llm


class DetectScopeCreep(Action):
    """Detect and prevent scope creep"""
    
    name: str = "DetectScopeCreep"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Scope Sentinel, an expert at detecting and preventing scope creep in freelance projects.

Analyze this request/situation for:
1. COMPARISON to original scope
2. IMPACT ASSESSMENT (time, cost, complexity)
3. CLASSIFICATION (In Scope / Gray Area / Out of Scope)
4. RESPONSE TEMPLATES
5. PRICING for additional work
6. DOCUMENTATION needed

Original scope/agreement:
{context}

New request/situation:
{content}

Provide professional responses that protect profitability while maintaining relationships.
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class ScopeSentinel(Role):
    """Scope Sentinel Agent - Scope creep detection"""
    
    name: str = "ScopeSentinel"
    profile: str = "Scope Management Specialist"
    goal: str = "Protect freelancers from scope creep and ensure fair compensation"
    constraints: str = "Be firm but diplomatic, document everything, suggest fair pricing"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([DetectScopeCreep])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await DetectScopeCreep().run(content=text, context=ctx)
