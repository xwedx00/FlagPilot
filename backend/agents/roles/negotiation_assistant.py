"""
Negotiation Assistant - Rate Negotiation Agent
"""

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from typing import ClassVar
from config import get_configured_llm


class AssistNegotiation(Action):
    """Help with rate and salary negotiations"""
    
    name: str = "AssistNegotiation"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Negotiation Assistant, an expert at helping freelancers negotiate better rates and terms.

Provide:
1. SITUATION ASSESSMENT
2. MARKET RATE ANALYSIS
3. NEGOTIATION STRATEGY
4. SCRIPTS for different scenarios
5. RESPONSES to common pushbacks
6. WALK-AWAY guidance

Negotiation situation:
{content}

Context (skills, experience, market):
{context}

Provide strategies and scripts that help freelancers get paid what they deserve.
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class NegotiationAssistant(Role):
    """Negotiation Assistant Agent - Rate negotiation"""
    
    name: str = "NegotiationAssistant"
    profile: str = "Negotiation Strategy Specialist"
    goal: str = "Help freelancers negotiate fair rates and terms"
    constraints: str = "Be realistic, know market rates, maintain professionalism"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AssistNegotiation])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await AssistNegotiation().run(content=text, context=ctx)
