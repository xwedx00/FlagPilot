"""
Talent Vet - Profile Evaluation Agent
"""

from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from typing import ClassVar
from config import get_configured_llm


class VetTalent(Action):
    """Evaluate freelancer profiles and portfolios"""
    
    name: str = "VetTalent"
    
    PROMPT_TEMPLATE: ClassVar[str] = """
You are Talent Vet, an expert at evaluating freelancer profiles and portfolios for clients.

Evaluate this profile/portfolio for:
1. PROFILE COMPLETENESS
2. PORTFOLIO QUALITY and authenticity
3. SKILL ALIGNMENT with project needs
4. RED FLAGS (fake work, stolen samples, inflated metrics)
5. INTERVIEW QUESTIONS to verify claims

Profile/Portfolio to evaluate:
{content}

Project requirements/context:
{context}

Provide:
- QUALITY SCORE (1-10)
- DETAILED EVALUATION
- SUGGESTED INTERVIEW QUESTIONS
- HIRING RECOMMENDATION
"""

    async def run(self, content: str, context: str = "") -> str:
        prompt = self.PROMPT_TEMPLATE.format(content=content, context=context)
        llm = get_configured_llm()
        return await llm.aask(prompt)


class TalentVet(Role):
    """Talent Vet Agent - Evaluates freelancer profiles"""
    
    name: str = "TalentVet"
    profile: str = "Talent Evaluation Specialist"
    goal: str = "Help clients find quality freelancers by evaluating profiles"
    constraints: str = "Be objective, verify claims, suggest verification methods"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([VetTalent])
    
    async def _act(self) -> Message:
        todo = self.rc.todo
        msg = self.rc.important_memory[-1] if self.rc.important_memory else None
        result = await todo.run(content=msg.content if msg else "", context="")
        return Message(content=result, role=self.profile, cause_by=type(todo), sent_from=self.name)
    
    async def analyze(self, text: str, context: dict = None) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return await VetTalent().run(content=text, context=ctx)
