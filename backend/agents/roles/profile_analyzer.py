"""
Profile Analyzer - Profile Optimization Agent
"""

import os
from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from metagpt.llm import LLM
from metagpt.config2 import Config
from typing import ClassVar
from loguru import logger


from config import get_configured_llm


class AnalyzeProfile(Action):
    """Optimize freelancer profiles"""
    
    name: str = "AnalyzeProfile"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Profile Analyzer, an expert at optimizing freelancer profiles for maximum visibility and client attraction.

Analyze this profile for:
1. HEADLINE effectiveness
2. SUMMARY/BIO impact
3. PORTFOLIO presentation
4. SKILLS and keywords optimization
5. RATE positioning
6. ACTIONABLE improvements

Profile to analyze:
{content}

Target clients/industry:
{context}

Provide specific, actionable improvements to increase profile visibility and conversion.
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class ProfileAnalyzer(Role):
    """Profile Analyzer Agent - Profile optimization"""
    
    name: str = "ProfileAnalyzer"
    profile: str = "Profile Optimization Specialist"
    goal: str = "Help freelancers create compelling profiles that attract ideal clients"
    constraints: str = "Be specific, suggest keywords, consider platform SEO"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([AnalyzeProfile])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await AnalyzeProfile().run(content=text, context=ctx)
