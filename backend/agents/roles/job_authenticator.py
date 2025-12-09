"""
Job Authenticator - Scam Detection Agent
"""

import os
from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from metagpt.llm import LLM
from metagpt.config2 import Config
from typing import ClassVar


from config import get_configured_llm


class AuthenticateJob(Action):
    """Detect fake job postings and scams"""
    
    name: str = "AuthenticateJob"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Job Authenticator, an expert at detecting fake job postings and protecting freelancers from scams.

Analyze this job posting/opportunity for:
1. RED FLAGS (definite scam indicators)
2. YELLOW FLAGS (concerning but not definitive)
3. GREEN FLAGS (legitimacy indicators)
4. Payment scam patterns (overpayment, check fraud, upfront fees)
5. Company/client verification needs

Job posting to analyze:
{content}

Additional context:
{context}

Provide:
- LEGITIMACY SCORE (1-10)
- DETAILED ANALYSIS of each flag found
- VERIFICATION STEPS recommended
- RECOMMENDATION (Apply / Proceed with Caution / Avoid)
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class JobAuthenticator(Role):
    """Job Authenticator Agent - Detects scams and fake job postings"""
    
    name: str = "JobAuthenticator"
    profile: str = "Scam Detection Specialist"
    goal: str = "Protect freelancers from fake job postings and scams"
    constraints: str = "Be vigilant, explain reasoning, suggest verification steps"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AuthenticateJob])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await AuthenticateJob().run(content=text, context=ctx)
