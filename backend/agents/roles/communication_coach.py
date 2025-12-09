"""
Communication Coach - Message Improvement Agent
"""

import os
from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from metagpt.llm import LLM
from metagpt.config2 import Config
from typing import ClassVar


from config import get_configured_llm


class CoachCommunication(Action):
    """Improve client communication"""
    
    name: str = "CoachCommunication"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Communication Coach, an expert at professional freelancer-client communication.

Analyze and improve:
1. MESSAGE ANALYSIS (tone, clarity, professionalism)
2. TONE ISSUES identification
3. IMPROVEMENTS suggested
4. ALTERNATIVE VERSIONS
5. REASONING explanation

Message/draft to review:
{content}

Context (client type, situation):
{context}

Provide improved versions that are clear, professional, and effective.
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class CommunicationCoach(Role):
    """Communication Coach Agent - Message improvement"""
    
    name: str = "CommunicationCoach"
    profile: str = "Professional Communication Specialist"
    goal: str = "Help freelancers communicate clearly and professionally"
    constraints: str = "Improve without changing meaning, consider cultural context"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([CoachCommunication])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await CoachCommunication().run(content=text, context=ctx)
