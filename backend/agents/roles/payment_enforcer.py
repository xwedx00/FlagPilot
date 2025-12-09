"""
Payment Enforcer - Payment Collection Agent
"""

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from typing import ClassVar
from config import get_configured_llm


class EnforcePayment(Action):
    """Create payment collection strategies"""
    
    name: str = "EnforcePayment"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Payment Enforcer, an expert at helping freelancers collect overdue payments professionally.

Analyze this payment situation and provide:
1. SITUATION ASSESSMENT (amount, days overdue, relationship)
2. RECOMMENDED APPROACH (friendly/formal/legal)
3. COMMUNICATION TEMPLATES (ready to use)
4. ESCALATION STEPS if needed
5. DOCUMENTATION needed

Situation:
{content}

Context (amount, days overdue, etc.):
{context}

Provide professional templates and strategies that maintain relationships while ensuring payment.
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class PaymentEnforcer(Role):
    """Payment Enforcer Agent - Payment collection strategies"""
    
    name: str = "PaymentEnforcer"
    profile: str = "Payment Collection Specialist"
    goal: str = "Help freelancers collect overdue payments professionally"
    constraints: str = "Maintain professionalism, preserve relationships, escalate appropriately"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([EnforcePayment])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await EnforcePayment().run(content=text, context=ctx)
